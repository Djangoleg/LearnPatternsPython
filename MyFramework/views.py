from lite_framework.settings import SERVER_URL
from lite_framework.templator import render
from patterns.architectural_pattern import UnitOfWork
from patterns.behavioral_patterns import ListView, CreateView, DeleteView, BaseSerializer, EmailNotifier, SmsNotifier
from patterns.structural_patterns import AppRoute, Debug
from patterns.сreational_patterns import Engine, Logger, Note, MapperRegistry

site = Engine()
logger = Logger('main')
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)

routes = {}


# Контроллер - о проекте.
@AppRoute(routes=routes, url='/about/')
class About:

    @Debug(name='About')
    def __call__(self, request):
        return '200 OK', render('about.html', data=request.get('data', None))


# Контроллер - стартовая страница.
@AppRoute(routes=routes, url='/')
class Index:

    @Debug(name='Index')
    def __call__(self, request):
        logger.log('Список заметок')

        mapper = MapperRegistry.get_current_mapper('note')
        notes = mapper.all()
        if notes:
            site.notes = notes

        if request.get('note', None):
            if request['note'] not in site.notes:
                site.notes.append(request['note'])

        return '200 OK', render('index.html', notes_list=site.notes, data=request.get('data', None))


# Контроллер - удалить заметку.
@AppRoute(routes=routes, url='/delete_note/')
class DeleteNote:

    @Debug(name='DeleteNote')
    def __call__(self, request):
        logger.log('Удалить заметку')
        try:
            id = int(request['request_params']['id'])

            note_mapper = MapperRegistry.get_current_mapper('note')
            note = note_mapper.find_by_id(id)
            category_id = note.category.id
            if note:
                note.mark_removed()
                UnitOfWork.get_current().commit()

            cat_mapper = MapperRegistry.get_current_mapper('category')
            category = cat_mapper.find_by_id(category_id)

            return '200 OK', render('note-list.html', data=request.get('data', None),
                                    objects_list=category.notes, name=category.name, id=category.id)
        except KeyError:
            return '200 OK', 'No note have been added yet'


# Контроллер - категории.
@AppRoute(routes=routes, url='/category/')
class Category:

    @Debug(name='Category')
    def __call__(self, request):
        mapper = MapperRegistry.get_current_mapper('category')
        categories = mapper.all()
        if categories:
            site.categories = categories

        return '200 OK', render('category.html', data=request.get('data', None), category_list=site.categories)


# Контроллер - создать категорию.
@AppRoute(routes=routes, url='/create-category/')
class CreateCategory:
    @Debug(name='CreateCategory')
    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост
            print(request)
            data = request['data']

            name = data['category_name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            new_category.mark_new()
            UnitOfWork.get_current().commit()

            cat_mapper = MapperRegistry.get_current_mapper('category')
            site.categories = cat_mapper.all()

            return '200 OK', render('category.html', data=request.get('data', None), category_list=site.categories)
        else:
            return '200 OK', render('create-category.html', data=request.get('data', None),
                                    category_list=site.categories)


# Контроллер - список заметок.
@AppRoute(routes=routes, url='/note-list/')
class NotesList:
    @Debug(name='NotesList')
    def __call__(self, request):
        logger.log('Список заметок')
        try:
            category = site.find_category_by_id(int(request['request_params']['id']))

            return '200 OK', render('note-list.html', data=request.get('data', None), objects_list=category.notes,
                                    name=category.name, id=category.id)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


# Контроллер - создать заметки.
@AppRoute(routes=routes, url='/create-note/')
class CreateNote:
    category_id = -1

    @Debug(name='CreateNote')
    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']

            name = data['note_name']
            name = site.decode_value(name)

            description = data['description']
            description = site.decode_value(description)

            category = None
            if self.category_id != -1:
                cat_mapper = MapperRegistry.get_current_mapper('category')
                category = cat_mapper.find_by_id(self.category_id)

                note_id = site.get_new_note_id()
                new_note = Note(name, description, category)
                new_note.id = note_id

                # Добавляем наблюдателей за заметкой
                new_note.observers.append(email_notifier)
                new_note.observers.append(sms_notifier)

                new_note.mark_new()
                UnitOfWork.get_current().commit()

                mapper = MapperRegistry.get_current_mapper('note')
                category_notes = mapper.get_by_category_id(self.category_id)

            return '200 OK', render('note-list.html', data=request.get('data', None),
                                    objects_list=category_notes, name=category.name, id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create-note.html', data=request.get('data', None),
                                        name=category.name, id=category.id)
            except KeyError:
                return '200 OK', 'No categories have been added yet'


# Контроллер - копировать заметку.
@AppRoute(routes=routes, url='/copy-note/')
class CopyNote:

    @Debug(name='CopyNote')
    def __call__(self, request):
        global category
        logger.log('Скопировать заметку')

        request_params = request['request_params']

        try:
            id = request_params['id']

            note_mapper = MapperRegistry.get_current_mapper('note')
            cat_mapper = MapperRegistry.get_current_mapper('category')

            old_note = note_mapper.find_by_id(id)
            if old_note:
                new_name = f'copy_{old_note.name}'
                new_note = old_note.clone()
                new_note.name = new_name

                new_note.mark_new()
                UnitOfWork.get_current().commit()

                site.notes = note_mapper.all()
                category = cat_mapper.find_by_id(new_note.category.id)

            return '200 OK', render('note-list.html', data=request.get('data', None),
                                    objects_list=category.notes, name=category.name, id=category.id)

        except KeyError:
            return '200 OK', 'No note have been added yet'


# Контроллер - читатели заметок.
@AppRoute(routes=routes, url='/reader-list/')
class ReaderListView(ListView, CreateView):
    # queryset = site.readers
    template_name = 'reader-list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('reader')
        return mapper.all()

    def create_obj(self, data: dict):
        name = data['reader_name']
        name = site.decode_value(name)
        new_obj = site.create_user('reader', name)
        site.readers.append(new_obj)
        new_obj.mark_new()
        UnitOfWork.get_current().commit()

# Контроллер - удалить пользователя.
@AppRoute(routes=routes, url='/delete-reader/')
class ReaderDeleteView(DeleteView):
    # queryset = site.readers
    template_name = 'reader-list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('reader')
        return mapper.all()

    def delete_obj(self, params: dict):
        reader_id = params.get('id', None)
        if reader_id:
            readers = self.get_queryset()
            for reader in readers:
                if reader.id == int(reader_id):
                    # site.readers.remove(reader)
                    reader.mark_removed()
                    UnitOfWork.get_current().commit()

# Контроллер - связь пользователя и заметки.
@AppRoute(routes=routes, url='/link-reader/')
class UserNote:

    @Debug(name='UserNote')
    def __call__(self, request):

        reader_mapper = MapperRegistry.get_current_mapper('reader')
        note_mapper = MapperRegistry.get_current_mapper('note')

        if request['method'] == 'POST':
            try:
                data = request['data']
                reader_id = data.get('link', None)
                check_box_values = [int(v) for k, v in data.items() if 'note_checkbox_' in k]

                if reader_id:
                    reader_id = int(reader_id)

                    note_mapper.clear_user_id(reader_id)
                    reader = reader_mapper.find_by_id(reader_id)

                    if reader:
                        for note_id in check_box_values:
                            for note in note_mapper.all():
                                if note.id == note_id:
                                    note_mapper.update_user_id(note_id, reader_id)

                        UnitOfWork.get_current().commit()
                        site.notes = note_mapper.all()

                    return '200 OK', render('link-reader.html', data=request.get('data', None),
                                            reader=reader, notes_list=site.notes)
            except KeyError:
                return '200 OK', 'No reader have been added yet'
        else:

            try:
                request_params = request['request_params']

                id = request_params.get('id', None)
                if id:
                    reader = reader_mapper.find_by_id(int(id))

                    site.notes = note_mapper.all()

                    return '200 OK', render('link-reader.html', data=request.get('data', None),
                                            reader=reader, notes_list=site.notes)

                else:
                    return '200 OK', 'No reader have been added yet'

            except KeyError:
                return '200 OK', 'No reader have been added yet'

@AppRoute(routes=routes, url='/api/')
class CourseApi:
    @Debug(name='CourseApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.notes).save()

class NotFound404:

    @Debug(name='NotFound404')
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'

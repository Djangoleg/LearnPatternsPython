from lite_framework.templator import render
from patterns.structural_patterns import AppRoute, Debug
from patterns.сreational_patterns import Engine, Logger, Note

site = Engine()
logger = Logger('main')
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

        if len(site.notes) == 0:
            # Add test notes data.
            cat_1 = site.create_category('common', None)
            site.categories.append(cat_1)

            note_test_1 = Note(name='map() function',
                               description='''
                                       # Return double of n<br>
                                       def addition(n):<br>
                                       return n + n<br>
                                       # We double all numbers using map()<br>
                                       numbers = (1, 2, 3, 4)<br>
                                       result = map(addition, numbers)<br>
                                       print(list(result))<br><br>
                                       # (('John', 'Jenny'), ('Charles', 'Christy'), ('Mike', 'Monica'))''',
                               category=cat_1)
            site.notes.append(note_test_1)

            note_test_2 = Note(name='zip() Function',
                               description='''
                                        a = ("John", "Charles", "Mike")<br>
                                        b = ("Jenny", "Christy", "Monica", "Vicky")<br>
                                        x = zip(a, b)<br>
                                        print(tuple(x))<br><br>
                        
                                        # (('John', 'Jenny'), ('Charles', 'Christy'), ('Mike', 'Monica'))''',
                               category=cat_1)
            site.notes.append(note_test_2)

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
            self.note_id = int(request['request_params']['id'])
            site.del_note_by_id(int(self.note_id))

            return '200 OK', render('index.html', notes_list=site.notes, data=request.get('data', None))
        except KeyError:
            return '200 OK', 'No note have been added yet'

# Контроллер - категории.
@AppRoute(routes=routes, url='/category/')
class Category:

    @Debug(name='Category')
    def __call__(self, request):
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

            site.categories.append(new_category)

            return '200 OK', render('category.html', data=request.get('data', None), category_list=site.categories)
        else:
            return '200 OK', render('create-category.html', data=request.get('data', None), category_list=site.categories)

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

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                note = site.create_note('common', name, 'todo description', category)
                site.notes.append(note)

            return '200 OK', render('note-list.html', data=request.get('data', None),
                                    objects_list=category.notes, name=category.name, id=category.id)

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
            # name = site.decode_value(name)
            old_note = site.find_note_by_id(int(id))
            if old_note:
                new_name = f'copy_{old_note.name}'
                new_id = site.get_new_note_id()
                new_note = old_note.clone()
                new_note.name = new_name
                new_note.id = new_id
                site.notes.append(new_note)
                category = site.find_category_by_id(new_note.category.id)
                category.notes.append(new_note)

            return '200 OK', render('note-list.html', data=request.get('data', None),
                                    objects_list=category.notes, name=category.name, id=category.id)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


class NotFound404:

    @Debug(name='NotFound404')
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'

from lite_framework.templator import render
from patterns.сreational_patterns import Engine, Logger, Note

site = Engine()
logger = Logger('main')

class About:
    def __call__(self, request):
        return '200 OK', render('about.html', data=request.get('data', None))

class NotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'

class Index:
    def __call__(self, request):
        logger.log('Список заметок')

        if len(site.notes) == 0:
            # Add test notes data.
            note_test_1 = Note(name='<b>map() function</b>',
                                   description='''
                                       # Return double of n<br>
                                       def addition(n):<br>
                                       return n + n<br>
                                       # We double all numbers using map()<br>
                                       numbers = (1, 2, 3, 4)<br>
                                       result = map(addition, numbers)<br>
                                       print(list(result))<br><br>
                                       # (('John', 'Jenny'), ('Charles', 'Christy'), ('Mike', 'Monica'))''',
                                   category='Common')
            site.notes.append(note_test_1)

            note_test_2 = Note(name='<b>zip() Function</b>',
                                   description='''
                                        a = ("John", "Charles", "Mike")<br>
                                        b = ("Jenny", "Christy", "Monica", "Vicky")<br>
                                        x = zip(a, b)<br>
                                        print(tuple(x))<br><br>
                        
                                        # (('John', 'Jenny'), ('Charles', 'Christy'), ('Mike', 'Monica'))''',
                                   category='Common')
            site.notes.append(note_test_2)

        if request.get('note', None):
            if request['note'] not in site.notes:
                site.notes.append(request['note'])

        return '200 OK', render('index.html', notes_list=site.notes, data=request.get('data', None))

class DeleteNote:
    def __call__(self, request):
        logger.log('Удалить заметку')
        try:
            self.note_id = int(request['request_params']['id'])
            site.del_note_by_id(int(self.note_id))

            return '200 OK', render('index.html', notes_list=site.notes, data=request.get('data', None))
        except KeyError:
            return '200 OK', 'No note have been added yet'

class CopyNote:
    def __call__(self, request):
        logger.log('Скопировать заметку')
        try:
            self.note_id = int(request['request_params']['id'])
            note = site.find_note_by_id(int(self.note_id))
            site.notes.append(note.clone())

            return '200 OK', render('index.html', notes_list=site.notes, data=request.get('data', None))
        except KeyError:
            return '200 OK', 'No note have been added yet'


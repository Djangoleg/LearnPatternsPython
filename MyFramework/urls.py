from datetime import date

from lite_framework.settings import SERVER_URL
from views import Index, About, DeleteNote, CopyNote


# front controller
def secret_front(request):
    data = request.get('data', dict())
    data['my_date'] = date.today().year
    data['server_url'] = SERVER_URL
    request['data'] = data

def other_front(request):
    data = request.get('data', dict())
    data['key'] = 'key'
    request['data'] = data

fronts = [secret_front, other_front]

routes = {
    '/': Index(),
    '/about/': About(),
    '/delete_note/': DeleteNote(),
    '/copy_note/': CopyNote(),
}

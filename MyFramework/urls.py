from datetime import date
from views import Index, About


# front controller
def secret_front(request):
    data = request.get('data', dict())
    data['my_date'] = date.today().year
    request['data'] = data



def other_front(request):
    data = request.get('data', dict())
    data['key'] = 'key'
    request['data'] = data

fronts = [secret_front, other_front]

routes = {
    '/': Index(),
    '/about/': About(),
}

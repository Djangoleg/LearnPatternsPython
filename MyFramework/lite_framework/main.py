import quopri

from lite_framework.lite_requests import PostRequests, GetRequests
from patterns.сreational_patterns import Note


class LiteFramework:
    """Класс Framework - основа фреймворка"""

    def __init__(self, routes_obj, fronts_obj):
        self.routes_lst = routes_obj
        self.fronts_lst = fronts_obj

    def __call__(self, environ, start_response):
        # Получаем адрес, по которому выполнен переход.
        path = environ['PATH_INFO']

        # Добавление закрывающего слеша.
        if not path.endswith('/'):
            path = f'{path}/'

        request = {}
        # Данные запроса.
        method = environ['REQUEST_METHOD']
        request['method'] = method

        if method == 'POST':
            data = PostRequests().get_request_params(environ)
            request['data'] = data

            name = data.get('name', None)
            description = data.get('description', None)
            category = data.get('category', None)

            if name and description and category:
                request['note'] = Note(name=name, description=description, category=category)

            print(f'Пришёл post-запрос: {LiteFramework.decode_value(data)}')
        if method == 'GET':
            request_params = GetRequests().get_request_params(environ)
            request['request_params'] = request_params
            print(f'Пришли GET-параметры: {request_params}')
        print(request)

        # Находим нужный контроллер
        # отработка паттерна page controller
        if path in self.routes_lst:
            view = self.routes_lst[path]
        else:
            view = PageNotFound404()

        # Наполняем словарь request элементами
        # этот словарь получат все контроллеры
        # отработка паттерна front controller.
        for front in self.fronts_lst:
            front(request)
        # Запуск контроллера с передачей объекта request.
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]

    @staticmethod
    def decode_value(data):
        new_data = {}
        for k, v in data.items():
            val = bytes(v.replace('%', '=').replace("+", " "), 'UTF-8')
            val_decode_str = quopri.decodestring(val).decode('UTF-8')
            new_data[k] = val_decode_str
        return new_data


# Новый вид WSGI-application.
# Первый — логирующий (такой же, как основной,
# только для каждого запроса выводит информацию
# (тип запроса и параметры) в консоль.
class DebugApplication(LiteFramework):

    def __init__(self, routes_obj, fronts_obj):
        self.application = LiteFramework(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        print('DEBUG MODE')
        print(env)
        return self.application(env, start_response)


# Новый вид WSGI-application.
# Второй — фейковый (на все запросы пользователя отвечает:
# 200 OK, Hello from Fake).
class FakeApplication(LiteFramework):

    def __init__(self, routes_obj, fronts_obj):
        self.application = LiteFramework(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'Hello from Fake']


class PageNotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'

from lite_framework.main import LiteFramework
from urls import routes, fronts
from wsgiref.simple_server import make_server

application = LiteFramework(routes, fronts)

with make_server('', 8080, application) as httpd:
    print("Запуск на порту 8080...")
    httpd.serve_forever()

from lite_framework.main import LiteFramework
from lite_framework.settings import HOST, PORT
from urls import routes, fronts
from wsgiref.simple_server import make_server


application = LiteFramework(routes, fronts)

with make_server(HOST, PORT, application) as httpd:
    print(f"Starting server http://{HOST}:{PORT}")
    httpd.serve_forever()

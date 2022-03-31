from lite_framework.main import LiteFramework
from urls import routes, fronts
from wsgiref.simple_server import make_server

HOST = '127.0.0.1'
PORT = 8080

application = LiteFramework(routes, fronts)

with make_server(HOST, PORT, application) as httpd:
    print(f"Starting server http://{HOST}:{PORT}")
    httpd.serve_forever()

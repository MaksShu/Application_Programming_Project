from config import *
from wsgiref.simple_server import make_server

with make_server('', 5000, app) as server:
    server.serve_forever()

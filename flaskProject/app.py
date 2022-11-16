from config import *
from wsgiref.simple_server import make_server


from blueprint import *


with make_server('', 5000, app) as server:
    app.register_blueprint(api_blueprint, url_prefix="/api/v1")
    app.register_blueprint(errors, url_prefix="/api/v1")
    server.serve_forever()


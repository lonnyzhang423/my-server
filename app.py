import argparse
import os

from flask import Flask, request

import helper
from api import RespData, MyResponse
from api.account import account
from api.admin import admin
from api.blog import blog
from api.location import location
from api.open import openapi
from database import db

db.init_tables()
app = Flask(__name__)
app.response_class = MyResponse

app.register_blueprint(account, url_prefix="/api")
app.register_blueprint(admin, url_prefix="/api/admin")
app.register_blueprint(blog, url_prefix="/api/blog")
app.register_blueprint(location, url_prefix="/api/user/<uid>")
app.register_blueprint(openapi, url_prefix="/api/open")


@app.before_request
def before_request_hook():
    helper.logger.info("%s : %s %s", request.remote_addr, request.method, request.url)
    helper.logger.info("Headers:%s%s", os.linesep, request.headers)


@app.errorhandler(404)
def page_not_found(e):
    data = RespData(code=404, message="Not Found").to_json()
    return MyResponse(status=404, response=data)


@app.errorhandler(405)
def method_not_allowed(e):
    data = RespData(code=405, message="Method Not Allowed").to_json()
    return MyResponse(status=405, response=data)


@app.errorhandler(500)
def server_internal_error(e):
    data = RespData(code=500, message="Internal Server Error").to_json()
    return MyResponse(status=500, response=data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--debug", type=bool, default=True)
    parser.add_argument("--threaded", type=bool, default=True)
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=args.threaded)

import os

from flask import Flask, request

import utils
from api.account import *
from db.database import init_db
from db.models import Response

app = Flask(__name__)

app.add_url_rule("/api/register", view_func=RegisterApi.as_view("register"))
app.add_url_rule("/api/login", view_func=LoginApi.as_view("login"))
app.add_url_rule("/api/logout", view_func=LogoutApi.as_view("logout"))
app.add_url_rule("/api/self", view_func=SelfApi.as_view("self"))


@app.before_request
def before_request_hook():
    utils.logger.info("%s : %s %s", request.remote_addr, request.method, request.url)
    utils.logger.info("Headers:%s%s", os.linesep, request.headers)

    params = request.values
    method = request.method
    path = request.path

    app_id = params.get("app_id")
    timestamp = params.get("timestamp")
    nonce = params.get("nonce")
    sig = params.get("signature")

    if not utils.valid_nonce(nonce):
        return Response(400, "Illegal nonce").to_json(), 400
    if not utils.valid_timestamp(timestamp):
        return Response(400, "Illegal timestamp").to_json(), 400
    if not utils.valid_app_id(app_id):
        return Response(400, "Illegal app_id").to_json(), 400
    if not utils.valid_signature(app_id, timestamp, nonce, method, path, sig):
        return Response(400, "Illegal signature").to_json(), 400


@app.errorhandler(404)
def page_not_found(e):
    return Response.e_404().to_json(), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return Response.e_405().to_json(), 405


@app.errorhandler(500)
def server_internal_error(e):
    return Response.e_500().to_json(), 500


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

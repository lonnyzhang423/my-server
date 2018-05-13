import hashlib
import hmac
import uuid

import requests

import utils

host = "http://localhost:5000"


def get_params():
    return {
        "timestamp": str(utils.timestamp()),
        "app_id": "root_app_id",
        "nonce": str(uuid.uuid4())
    }


def common_params(method=None, path=None, app_id="root_app_id", app_secret="root_app_secret"):
    ts = str(utils.timestamp())
    nonce = str(uuid.uuid4())
    msg = (method + path + "?app_id=" + app_id + "&nonce=" + nonce + "&timestamp=" + ts).encode("utf8")
    app_secret = app_secret.encode("utf8")
    sig = hmac.new(app_secret, msg, hashlib.sha256).hexdigest()
    return {"timestamp": str(ts), "app_id": app_id, "nonce": nonce, "signature": sig}


def register():
    path = "/api/register"
    url = host + path
    params = common_params("POST", path)
    params["register_type"] = "phone"
    params["username"] = "18899990000"
    params["password"] = "password"
    resp = requests.post(url, data=params, timeout=3).json()
    print(resp)


def login():
    path = "/api/login"
    url = host + path
    params = common_params("POST", path)
    params["login_type"] = "phone"
    params["username"] = "18899990000"
    params["password"] = "password"
    resp = requests.post(url, data=params).json()
    print(resp)


def update_self():
    path = "/api/self"
    url = host + path
    params = common_params("PUT", path)
    params["uid"] = "b2ec2366fbf845498ce8cc78755325bb"
    params["nickname"] = "foo_user"
    params["gender"] = 1
    params["headline"] = "this is headline"
    headers = {"Authorization": "Bearer e0b2eb56-0c10-4a82-b1f0-8de7a818ebe5"}
    resp = requests.put(url, headers=headers, data=params).json()
    print(resp)


def get_self():
    path = "/api/self"
    url = host + path + "?"
    params = common_params("GET", path)
    params["uid"] = "751069bc779440f190fd20c6b2cde3cd"
    for k, v in params.items():
        url += k + "=" + v + "&"
    url = url[:-1]
    print(url)
    headers = {"Authorization": "Bearer fc2bca23-e1e0-4d32-a140-3c6384b773de"}
    resp = requests.get(url, headers=headers).json()
    print(resp)


def get_headers():
    path = "/api/utils/headers"
    url = host + path
    resp = requests.get(url).json()
    print(resp)


if __name__ == '__main__':
    # register()
    # login()
    # get_self()
    # update_self()
    # get_self()
    pass

import json

import requests

from database import db, session_scope
from database.models import Movie

host = "http://localhost:5000"
headers = {'Content-Type': 'application/json',
           "Authorization": "Bearer 1c75b01b-e306-4509-8d7e-fad50d6078ef"}


def register():
    path = "/api/register"
    url = host + path
    params = json.dumps({"register_type": "phone", "username": "18899910000", "password": "password"})
    resp = requests.post(url, data=params, headers=headers).json()
    print(resp)


def login():
    path = "/api/login"
    url = host + path
    params = json.dumps({"login_type": "phone", "username": "18899990000", "password": "password"})
    resp = requests.post(url, data=params, headers=headers).json()
    print(resp)


def admin_register():
    path = "/api/admin/register"
    url = host + path
    params = json.dumps({"username": "lonnyzhang", "password": "lonnyzhang423"})
    resp = requests.post(url, data=params, headers=headers).json()
    print(resp)


def admin_login():
    path = "/api/admin/login"
    url = host + path
    params = json.dumps({"username": "lonnyzhang", "password": "lonnyzhang423"})
    resp = requests.post(url, headers={'Content-Type': 'application/json'}, data=params).json()
    print(resp)


def update_self():
    path = "/api/self"
    url = host + path
    params = json.dumps(
        {"uid": "751069bc779440f190fd20c6b2cde3cd",
         "nickname": "foo_user",
         "gender": 1,
         "headline": "this is headline"})
    resp = requests.put(url, headers=headers, data=params).json()
    print(resp)


def get_self():
    path = "/api/self"
    url = host + path
    resp = requests.get(url, headers=headers).json()
    print(resp)


def get_headers():
    path = "/api/open/anything"
    url = host + path
    resp = requests.get(url).json()
    print(resp)


def get_movies():
    path = "/api/open/movies"
    url = host + path
    resp = requests.get(url).json()
    print(resp)


def post_location():
    path = "/api/user/751069bc779440f190fd20c6b2cde3cd/location"
    url = host + path
    params = json.dumps({"uid": "751069bc779440f190fd20c6b2cde3cd",
                         "longitude": "123.1231231231",
                         "latitude": "23.11111111"})
    resp = requests.post(url, data=params, headers=headers).json()
    print(resp)


def insert_movie():
    db.init_tables()

    def compose_movie(item):
        title = item["title"]
        original_title = item["original_title"]
        directors = ",".join([d["name"] for d in item["directors"]])
        casts = ",".join([c["name"] for c in item["casts"]])
        year = item["year"]
        genres = ",".join(item["genres"])
        image = item["images"]["small"]
        rating = item["rating"]["average"]
        return Movie(title, original_title, directors, casts, year, genres, image, rating)

    offset = 0
    count = 20
    while offset < 250:
        url = "https://api.douban.com/v2/movie/top250?start={}&count={}".format(offset, count)
        print(url)
        resp = requests.get(url).json()
        for item in resp["subjects"]:
            m = compose_movie(item)
            with session_scope() as session:
                session.add(m)
        offset += count


def post_article(i):
    path = "/api/blog/articles"
    url = host + path + "?"
    content = """#### 基本信息
* **学校**：南京邮电大学
* **学历**：本科、2016届
* **专业**：软件工程、绩点top2
* **知乎**：[lonnyzhang](https://www.zhihu.com/people/lonnyzhang/activities)
* **Github**：[lonnyzhang423](https://github.com/lonnyzhang423)
* **邮箱**：lonnzhang423@gmail.com
#### 专业技能
* **Android**：两年实际开发经验。理解`Android`体系架构，熟练掌握组件使用、界面绘制、多线程操作、数据存储等；熟练使用`RxJava`、`Retrofit`等第三方框架；
* **Python**：一年使用经验。结合`TensorFlow`识别知乎验证码，短时间爬取上亿条数据；结合`Mysql`、`Redis`等开发了一套`Restful api`；
* **前端**：熟悉`html`、`css`、`js`的基本用法。使用`ReactJS`结合`Python`的`Restful api`开发了前后端分离的这个网站；
* **其他**：熟练使用`Git`、`Android Studio`、`WebStorm`、`PyCharm`等开发工具；熟练阅读英文开发文档
#### 工作经历
* **2016/03-至今** 东方财富网 `Android`客户端开发维护
* **2015/09-2015/11** 公平价二手车 `Android`客户端开发维护（实习）
"""
    data = json.dumps({"title": "this is title " + str(i), "intro": "markdown intro", "content": content})
    resp = requests.post(url, data=data, headers=headers).json()
    print(resp)


def get_articles():
    path = "/api/blog/articles"
    url = host + path
    resp = requests.get(url, headers=headers).json()
    print(resp)


def get_article(aid):
    path = "/api/blog/articles/{}".format(aid)
    url = host + path
    resp = requests.get(url, headers=headers).json()
    print(resp)


def update_article(aid):
    path = "/api/blog/articles/{}".format(aid)
    url = host + path
    data = json.dumps({"title": "title",
                       "intro": "modified markdown intro",
                       "content": "## title\n> this is quote"})
    resp = requests.put(url, data=data, headers=headers).json()
    print(resp)


if __name__ == '__main__':
    # login()
    # admin_register()
    # admin_login()
    # for i in range(9):
    #     post_article("1")
    get_article("41")
    update_article("41")
    # get_article("1")
    # post_article("1")

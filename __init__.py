import requests

from database import db, session_scope
from database.models import Movie


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


def start():
    db.init_tables()

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


if __name__ == '__main__':
    start()

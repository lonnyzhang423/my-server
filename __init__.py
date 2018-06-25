import requests

from db.database import init_db, session_scope
from db.models import Movie


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
    init_db()

    session = requests.session()
    start = 0
    count = 20
    while start < 250:
        url = "https://api.douban.com/v2/movie/top250?start={}&count={}".format(start, count)
        print(url)
        resp = session.get(url).json()
        for item in resp["subjects"]:
            m = compose_movie(item)
            with session_scope() as session:
                session.add(m)
        start += count


if __name__ == '__main__':
    start()

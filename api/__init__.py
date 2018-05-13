from flask.views import MethodView

from db.models import Response


class BaseMethodView(MethodView):

    # noinspection PyBroadException
    def dispatch_request(self, *args, **kwargs):
        try:
            return super().dispatch_request(*args, **kwargs)
        except BaseException:
            return Response.e_500().to_json(), 500
import json
from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.decorators import method_decorator

from cutting_board.client import Client

from ..decorators import basic_auth


peeler_auth = basic_auth(settings.PEELER_BASIC_AUTH_USERNAME,
                         settings.PEELER_BASIC_AUTH_PASSWORD,
                         settings.PEELER_BASIC_AUTH_REALM)


@method_decorator(csrf_exempt, name='dispatch')
class PeelerAPIListView(View):
    http_method_names = ['post']

    # noinspection PyMethodMayBeStatic
    @method_decorator(peeler_auth)
    def post(self, request: HttpRequest, *_args, **_kwargs):
        client = Client(settings.CUTTING_BOARD_URL)
        docs = json.loads(request.body)
        if not isinstance(docs, list):
            return HttpResponseBadRequest('Wrong data type')
        if len(docs) > 500:
            return HttpResponseBadRequest('Too many recipes in a batch')
        client.add_recipe(docs)
        return HttpResponse(status=201)

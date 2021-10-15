import json
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.decorators import method_decorator

from cutting_board.client import Client


@method_decorator(csrf_exempt, name='dispatch')
class PeelerAPIListView(View):
    http_method_names = ['post']

    # noinspection PyMethodMayBeStatic
    def post(self, request: HttpRequest, *_args, **_kwargs):
        client = Client('http://localhost:8983/solr/recipe')
        docs = json.loads(request.body)
        if not isinstance(docs, list):
            return HttpResponseBadRequest('Wrong data type')
        if len(docs) > 500:
            return HttpResponseBadRequest('Too many recipes in a batch')
        client.add_recipe(docs)
        return HttpResponse(status=201)

from django.views.generic import View
from django.http.request import HttpRequest
from django.http.response import JsonResponse

from cutting_board.client import Client


class PeelerAPIDetailView(View):
    http_method_names = ['get', 'delete']

    # noinspection PyMethodMayBeStatic
    def get(self, request: HttpRequest, *args, **kwargs):
        client = Client('http://localhost:8983/solr/recipe')
        recipe_id = kwargs.get('recipe_id', 'none')
        return JsonResponse(client.get_recipe(recipe_id))

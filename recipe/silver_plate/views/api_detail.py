from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.decorators import method_decorator

from cutting_board.client import Client

from ..decorators import basic_auth


peeler_auth = basic_auth(settings.PEELER_BASIC_AUTH_USERNAME,
                         settings.PEELER_BASIC_AUTH_PASSWORD,
                         settings.PEELER_BASIC_AUTH_REALM)


@method_decorator(csrf_exempt, name='dispatch')
class PeelerAPIDetailView(View):
    http_method_names = ['get', 'delete']

    # noinspection PyMethodMayBeStatic
    @method_decorator(peeler_auth)
    def get(self, _request: HttpRequest, *_args, **kwargs):
        client = Client(settings.CUTTING_BOARD_URL)
        recipe_id = kwargs.get('recipe_id')
        return JsonResponse(client.get_recipe(recipe_id))

    # noinspection PyMethodMayBeStatic
    @method_decorator(peeler_auth)
    def delete(self, _request: HttpRequest, *_args, **kwargs):
        client = Client(settings.CUTTING_BOARD_URL)
        recipe_id = kwargs.get('recipe_id')
        client.delete_recipe(recipe_id)
        return HttpResponse(status=204)

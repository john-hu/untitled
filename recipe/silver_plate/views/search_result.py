import math
from typing import List, Optional

from django.conf import settings
from django.views.generic import TemplateView

from cutting_board.client import Client

PAGE_SIZE = 16
EASY_PREPARE_COUNTS = 5
EASY_COOK_TIME = 600
# Looks like we only have these two kinds in our db
DIET_LABELS = ["GlutenFreeDiet", "VegetarianDiet"]


class SearchResultView(TemplateView):
    template_name = 'search_result.html'

    def _prepare_query_filter(self) -> List[str]:
        vegetarian = self.request.GET.get('vegetarian', None) == 'true'
        easy_prepare = self.request.GET.get('easy_prepare', None) == 'true'
        easy_cook = self.request.GET.get('easy_cook', None) == 'true'
        diet_search = self.request.GET.get('diet_search', None) == "true"

        filters = []
        if vegetarian:
            filters.append('vegetarian')
        if easy_prepare:
            filters.append(f'ingredientsCount:[* TO {EASY_PREPARE_COUNTS}]')
        if easy_cook:
            filters.append(f'cookTime: [* TO {EASY_COOK_TIME}]')
        if diet_search:
            filters.append(f'suitableForDiet:({" OR ".join(DIET_LABELS)})')

        return filters

    @staticmethod
    def search(user_query: Optional[str], page_index: int, filters: List[str]):
        client = Client(settings.CUTTING_BOARD_URL)
        is_random = False
        if user_query:
            search_result = client.search_recipe(user_query, page_index, PAGE_SIZE, filters)
            if search_result['hits'] < 1:
                is_random = True
                search_result = client.random_recipe()
        else:
            is_random = True
            search_result = client.random_recipe()
        return search_result, is_random

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # get parameters
        user_query = self.request.GET.get('q', None)
        page_index = int(self.request.GET.get('p', 0))
        filters = self._prepare_query_filter()
        search_result, is_random = self.search(user_query, page_index, filters)
        # total search pages
        pages = math.ceil(search_result['hits'] / PAGE_SIZE)
        # prepare data
        context['query'] = user_query
        context['total_hits'] = search_result['hits']
        context['page_index'] = page_index
        context['search_result'] = search_result
        context['is_random'] = is_random
        context['prev_index'] = -1 if page_index == 0 else page_index - 1
        context['next_index'] = -1 if page_index > pages - 2 else page_index + 1
        if page_index >= pages and search_result['hits'] > 0:
            context['redirect_page0'] = True
            # out of page cases, we should redirect back to the first page.
            return context
        elif search_result['hits'] == 0 or is_random:
            return context
        # prepare pagination: 5 pages at most
        # reserve two pages before page_index
        start_index = page_index - 2 if page_index - 2 > -1 else 0
        if pages - page_index < 3:
            # If the page_index is near to the end, we should keep the start page at the page - 5.
            # Think about a case pages 7 and at page 6, we will give start index more
            start_index = max(0, pages - 5)
        # reserve two pages after page_index
        end_index = page_index + 3 if page_index + 3 < pages else pages
        if page_index < 3:
            end_index = min(pages, 5)
        context['pages'] = [{'index': index,
                             'label': index + 1,
                             'disabled': index == page_index} for index in range(start_index, end_index)]
        return context

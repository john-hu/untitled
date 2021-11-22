import math

from django.conf import settings
from django.views.generic import TemplateView

from cutting_board.client import Client

PAGE_SIZE = 16
EASY_PREPARE_COUNTS = 5


class SearchResultView(TemplateView):
    template_name = "search_result.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # get parameters
        user_query = self.request.GET.get('q', None)
        page_index = int(self.request.GET.get('p', 0))
        easy_prepare = self.request.GET.get("easy_prepare", None) == "true"
        vegetarian = self.request.GET.get("vegetarian", None) == "true"

        raw_query = f"+{user_query}"
        if vegetarian:
            raw_query = f"+vegetarian {raw_query}"
        if easy_prepare:
            raw_query = f"+ingredientsCount:[* TO {EASY_PREPARE_COUNTS}] {raw_query}"
        if not user_query:
            return context
        search_result = Client(settings.CUTTING_BOARD_URL).search_recipe(raw_query, page_index, PAGE_SIZE)
        # total search pages
        pages = math.ceil(search_result['hits'] / PAGE_SIZE)
        # prepare data
        context['query'] = user_query
        context['total_hits'] = search_result['hits']
        context['page_index'] = page_index
        context['search_result'] = search_result
        context['prev_index'] = -1 if page_index == 0 else page_index - 1
        context['next_index'] = -1 if page_index > pages - 2 else page_index + 1
        if page_index >= pages and search_result['hits'] > 0:
            context['redirect_page0'] = True
            # out of page cases, we should redirect back to the first page.
            return context
        elif search_result['hits'] == 0:
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

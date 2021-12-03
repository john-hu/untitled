from django.urls import path
from django.views.generic import TemplateView

from .views.api_detail import PeelerAPIDetailView
from .views.api_list import PeelerAPIListView
from .views.search import SearchView
from .views.search_result import SearchResultView

urlpatterns = [
    path('peeler/<path:recipe_id>', PeelerAPIDetailView.as_view()),
    path('peeler/', PeelerAPIListView.as_view()),
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='robots.txt',
            content_type='text/plain')),
    path(
        'sitemap.xml',
        TemplateView.as_view(
            template_name='sitemap.xml',
            content_type='application/xml')),
    path('', SearchView.as_view()),
    path('search', SearchResultView.as_view()),
]

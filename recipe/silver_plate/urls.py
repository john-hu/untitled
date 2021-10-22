from django.urls import path

from .views.api_detail import PeelerAPIDetailView
from .views.api_list import PeelerAPIListView
from .views.search import SearchView
from .views.search_result import SearchResultView

urlpatterns = [
    path('peeler/<path:recipe_id>', PeelerAPIDetailView.as_view()),
    path('peeler/', PeelerAPIListView.as_view()),
    path('', SearchView.as_view()),
    path('search', SearchResultView.as_view()),
]

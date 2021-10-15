from django.urls import path

from .views.api_detail import PeelerAPIDetailView
from .views.api_list import PeelerAPIListView

urlpatterns = [
    path("peeler/<path:recipe_id>", PeelerAPIDetailView.as_view()),
    path("peeler/", PeelerAPIListView.as_view())
]

from django.urls import path

from .views.api_detail import PeelerAPIDetailView

urlpatterns = [
    path("peeler/<str:recipe_id>", PeelerAPIDetailView.as_view())
]

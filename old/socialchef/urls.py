from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views.root_view import RootView
from .views.test_view import UserViewSet

router = DefaultRouter()
router.register('', UserViewSet)

urlpatterns = [
    path('', RootView.as_view()),
    path('test/', include(router.urls)),
]

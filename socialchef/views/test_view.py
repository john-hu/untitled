from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet
from ..serializers.test_serializer import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        print(f'user: {request.user}')
        return super().list(request=request, args=args, kwargs=kwargs)

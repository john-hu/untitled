"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path


urlpatterns = [
    # for add a test app locally
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('rest/', include('rest_framework.urls')),  # for login superuser
    path('api/auth/', include('rest_framework_social_oauth2.urls')),  # for test authentication
    # end of test
    path('', include('socialchef.urls')),
]

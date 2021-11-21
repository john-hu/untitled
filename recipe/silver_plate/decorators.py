import base64

from django.http import HttpResponse


def basic_auth(username: str, password: str, realm: str):
    # first layer: use scope to store username and password
    def wrapper(view):
        # real wrapper
        def impl(request, *args, **kwargs):
            # check basic auth
            if 'HTTP_AUTHORIZATION' in request.META:
                auth = request.META['HTTP_AUTHORIZATION'].split()
                if len(auth) == 2:
                    if auth[0].lower() == "basic":
                        header_username, header_password = base64.b64decode(auth[1]).decode('utf8').split(':', 1)
                        if username == header_username and password == header_password:
                            request.user = username
                            return view(request, *args, **kwargs)
            # Otherwise, return 401 unauthorized
            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = f'Basic realm="{realm}"'
            return response

        return impl

    return wrapper

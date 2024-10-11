from django.conf import settings

from kukkuu.oidc import BrowserTestAwareJWTAuthentication

jwt_settings = settings.GRAPHQL_JWT


# Copied from https://github.com/flavors/django-graphql-jwt/blob/0debe4fbd5299e394ee253e6fa77e7a68b3236ba/graphql_jwt/utils.py#L63 #noqa
def get_http_authorization(request):
    auth = request.META.get(jwt_settings["JWT_AUTH_HEADER_NAME"], "").split()
    prefix = jwt_settings["JWT_AUTH_HEADER_PREFIX"]

    if len(auth) != 2 or auth[0].lower() != prefix.lower():
        return request.COOKIES.get(jwt_settings["JWT_COOKIE_NAME"])
    return auth[1]


# Copied from https://github.com/flavors/django-graphql-jwt/blob/0debe4fbd5299e394ee253e6fa77e7a68b3236ba/graphql_jwt/middleware.py#L30 # noqa
def _authenticate(request):
    is_anonymous = not hasattr(request, "user") or request.user.is_anonymous
    return is_anonymous and get_http_authorization(request) is not None


# copied from https://github.com/City-of-Helsinki/open-city-profile/blob/4f46f9f9f195c4254f79f5dfbd97d03b7fa87a5b/open_city_profile/middleware.py#L6  # noqa
class JWTAuthentication:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if _authenticate(request):
            try:
                authenticator = BrowserTestAwareJWTAuthentication()
                user_auth = authenticator.authenticate(request)
                if user_auth is not None:
                    request.user_auth = user_auth
                    request.user = user_auth.user
            except Exception as e:
                request.auth_error = e

        return self.get_response(request)

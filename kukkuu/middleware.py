from kukkuu.oidc import BrowserTestAwareJWTAuthentication


# copied from https://github.com/City-of-Helsinki/open-city-profile/blob/4f46f9f9f195c4254f79f5dfbd97d03b7fa87a5b/open_city_profile/middleware.py#L6  # noqa
class JWTAuthentication:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            try:
                authenticator = BrowserTestAwareJWTAuthentication()
                user_auth = authenticator.authenticate(request)
                if user_auth is not None:
                    request.user_auth = user_auth
                    request.user = user_auth.user
            except Exception as e:
                request.auth_error = e

        return self.get_response(request)

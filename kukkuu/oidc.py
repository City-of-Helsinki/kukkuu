from helusers.oidc import RequestJWTAuthentication


class GraphQLApiTokenAuthentication(RequestJWTAuthentication):
    """
    Custom wrapper for the helusers.oidc.RequestJWTAuthentication backend.
    Needed to make it work with graphql_jwt.middleware.JSONWebTokenMiddleware,
    which in turn calls django.contrib.auth.middleware.AuthenticationMiddleware.
    Authenticate function should:
    1. accept kwargs, or django's auth middleware will not call it
    2. return only the user object, or django's auth middleware will fail
    """

    def authenticate(self, request, **kwargs):
        user_authorization = super().authenticate(request)
        return user_authorization.user if user_authorization else None

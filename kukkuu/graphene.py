from helusers.oidc import AuthenticationError
from jose import ExpiredSignatureError

from kukkuu.exceptions import AuthenticationExpiredError

SCHEMA_INTROSPECTION_OPERATION = "operation_definition"
SCHEMA_INTROSPECTION_OPERATION_NAME = "IntrospectionQuery"


# pretty much copied from https://github.com/City-of-Helsinki/open-city-profile/blob/4f46f9f9f195c4254f79f5dfbd97d03b7fa87a5b/open_city_profile/graphene.py#L18  # noqa
class JWTMiddleware:
    def resolve(self, next, root, info, **kwargs):
        request = info.context

        auth_error = getattr(request, "auth_error", None)
        if isinstance(auth_error, Exception):
            # The GraphQL schema introspection can be allowed for unauthenticated users
            if (
                info.operation.kind == SCHEMA_INTROSPECTION_OPERATION
                and info.operation.name.value == SCHEMA_INTROSPECTION_OPERATION_NAME
            ):
                return next(root, info, **kwargs)

            # TODO with the current version of django-helusers (v0.7.0) there is no
            # proper way to catch only expired token errors, so this kind of hax is
            # needed for that. If/when helusers offers a way to do this properly
            # this implementation should be changed.
            if isinstance(auth_error, AuthenticationError) and isinstance(
                auth_error.__context__, ExpiredSignatureError
            ):
                raise AuthenticationExpiredError(
                    "Invalid Authorization header. JWT has expired."
                ) from auth_error
            raise auth_error

        return next(root, info, **kwargs)

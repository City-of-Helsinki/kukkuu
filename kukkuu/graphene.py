# copied from https://github.com/City-of-Helsinki/open-city-profile/blob/4f46f9f9f195c4254f79f5dfbd97d03b7fa87a5b/open_city_profile/graphene.py#L18  # noqa
class JWTMiddleware:
    def resolve(self, next, root, info, **kwargs):
        request = info.context

        auth_error = getattr(request, "auth_error", None)
        if isinstance(auth_error, Exception):
            raise auth_error

        return next(root, info, **kwargs)

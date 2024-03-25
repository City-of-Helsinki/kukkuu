from functools import wraps
from typing import Callable, Optional

from django.core.exceptions import PermissionDenied

from common.utils import context
from verification_tokens.models import VerificationToken


def user_from_auth_verification_token_when_denied(
    get_token: Callable[[dict], Optional[str]]
):
    """Sets the related auth token user to the context
    (in place of the logged in user; ``context.user``),
    if the wrapped function throws a permission denied error and then retries
    the wrapped function.

    This decorator is implemented to be used with the ``@login_required`` decorator
    in the GraphQL endpoint's handler.

    Example
    =======
    In this example, the decorator first executes the ``@login_required``,
    and then if it raises the ``PermissionDenied`` error,
    the ``"auth_token"`` is used from the input variables to find
    an authorization verification token that links to an user that
    the token represents
    >>> # doctest: +SKIP
    ... # When the login_required raises a PermissionDenied exception,
    ... # use the auth_token from the input variables
    ... # to populate the context.user with the token related user
    ... # and then try again.
    ... @user_from_auth_verification_token_when_denied(
    ...     get_token=lambda variables: variables.get("auth_token", None)
    ... )
    ... @login_required
    ... def mutate_and_get_payload(cls, root, info, **kwargs):
    ...     pass

    The input in this example would be
    >>> # doctest: +SKIP
    ... {
    ...     "input": {
    ...         "authToken": auth_verification_token.key,
    ...     }
    ... }

    Args:
        get_token ((dict) -> str | None): a (lambda) function that
                returns an auth token from the input variables # noqa
    """

    def _get_verification_token(**kwargs):
        if auth_verification_token_key := get_token(kwargs):
            return VerificationToken.objects.filter(
                key=auth_verification_token_key,
                verification_type=VerificationToken.VERIFICATION_TYPE_SUBSCRIPTIONS_AUTH,  # noqa E501
            ).first()

    def _set_user_to_context(context, user):
        context.user = user

    def decorator(func):
        @wraps(func)
        @context(func)
        def wrapper(context, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PermissionDenied as permissionDeniedError:
                if auth_verification_token := _get_verification_token(**kwargs):
                    _set_user_to_context(
                        context, auth_verification_token.content_object
                    )
                    return func(*args, **kwargs)
                else:
                    raise permissionDeniedError

        return wrapper

    return decorator

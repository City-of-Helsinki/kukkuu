from auditlog.context import set_actor
from auditlog.middleware import AuditlogMiddleware as _AuditlogMiddleware
from django.utils.functional import SimpleLazyObject


class AuditlogMiddleware(_AuditlogMiddleware):
    """
    Extends the `auditlog.middleware.AuditlogMiddleware` to fix an issue
    with setting the actor in the audit log context.

    This middleware ensures that the actor in the audit log context is
    correctly set to the current user and their remote address, addressing
    a potential issue where the actor might not be available when
    `auditlog` attempts to access it.

    This fix is based on the suggestion provided in:
    https://github.com/jazzband/django-auditlog/issues/115#issuecomment-1682234986
    """

    def __call__(self, request):
        """
        Processes the request and sets the actor in the audit log context.

        This method overrides the base `__call__` method to ensure that
        the actor is correctly set before the request is processed.

        Args:
            request: The incoming HTTP request.

        Returns:
            The response from the next middleware or view.
        """
        remote_addr = self._get_remote_addr(request)
        user = SimpleLazyObject(lambda: getattr(request, "user", None))

        context = set_actor(actor=user, remote_addr=remote_addr)

        with context:
            return self.get_response(request)  # type: ignore

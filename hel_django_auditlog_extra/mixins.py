from contextvars import ContextVar

from auditlog.signals import accessed

# Create a ContextVar to store the accessed flag
_auditlog_accessed_sent = ContextVar("_auditlog_accessed_sent", default=False)


class AuditlogAdminViewAccessLogMixin:
    """
    A mixin for Django Admin views to log access events using `django-auditlog`.

    This mixin automatically logs accesses to the `change_view`, `history_view`,
    and `delete_view` in the Django Admin. It also provides an option to log
    accesses to the `changelist_view` (list view).

    By default, only access to individual object views (change, history, delete)
    is logged. To enable logging for the list view, set the
    `enable_list_view_audit_logging` attribute to `True` in your `ModelAdmin`.
    Please note that this will trigger a very intensive logging and a lots of
    access log data will be created and stored!

    Attributes:
        enable_list_view_audit_logging (bool):
            A flag to enable/disable logging access from the list view.
            Defaults to `False`.

    Example:

        ```python
        from django.contrib import admin
        from .models import MyModel


        @admin.register(MyModel)
        class MyModelAdmin(AuditlogAdminViewAccessLogMixin, admin.ModelAdmin):
            enable_list_view_audit_logging = True  # Enable list view logging
            # ... other admin configurations ...
        ```
    """

    # To write access log to audit log of each instance in the admin list view
    enable_list_view_audit_logging = False

    def changelist_view(self, request, extra_context=None):
        """
        Handles the changelist view (list view) and logs access events for
        objects on the current page if `enable_list_view_audit_logging` is `True`.

        The changelist in the response's context_data (i.e. "cl") should be set by the
        super().changelist_view call, see e.g.
        https://github.com/django/django/blob/4.2.16/django/contrib/admin/options.py#L2071

        Args:
            request: The HTTP request object.
            extra_context: Optional extra context to pass to the template.

        Returns:
            The response from the superclass's `changelist_view` method.
        """
        response = super().changelist_view(request, extra_context)
        if self.enable_list_view_audit_logging:
            changelist = response.context_data["cl"]
            for obj in changelist.result_list:
                accessed.send(sender=obj.__class__, instance=obj, actor=request.user)
        return response

    def get_object(self, request, object_id, from_field=None):
        """
        Retrieves the object for the admin view and sends the `accessed` signal.

        This method overrides the default `get_object` to include sending the
        `accessed` signal from `django-auditlog`. It uses a `ContextVar` to
        ensure the signal is sent only once per request, even if `get_object`
        is called multiple times.

        Args:
            request: The HTTP request object.
            object_id: The ID of the object to retrieve.
            from_field: The field to use to retrieve the object.

        Returns:
            The retrieved object, or None if the object does not exist.
        """
        accessed_sent = _auditlog_accessed_sent.get()
        obj = super().get_object(request, object_id, from_field)
        if obj is not None and not accessed_sent:
            accessed.send(sender=obj.__class__, instance=obj, actor=request.user)
            # get_object can be called multiple times,
            # so prevent signalling the accessed,
            # if it has already been signalled.
            _auditlog_accessed_sent.set(True)
        return obj

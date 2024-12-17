from auditlog.signals import accessed


class AuditlogAdminViewAccessLogMixin:
    """
    A mixin for Django Admin views to log access events using `django-auditlog`.

    This mixin automatically logs accesses to the `change_view`, `history_view`,
    and `delete_view` in the Django Admin. It also provides an option to log
    accesses to the `changelist_view` (list view).

    By default, only access to individual object views (change, history, delete)
    is logged. To enable logging for the list view, set the
    `write_accessed_from_list_view` attribute to `True` in your `ModelAdmin`.
    Please note that this will trigger a very intensive logging and a lots of
    access log data will be created and stored!

    Attributes:
        write_accessed_from_list_view (bool):
            A flag to enable/disable logging access from the list view.
            Defaults to `False`.

    Example:

        ```python
        from django.contrib import admin
        from .models import MyModel


        @admin.register(MyModel)
        class MyModelAdmin(AuditlogAdminViewAccessLogMixin, admin.ModelAdmin):
            write_accessed_from_list_view = True  # Enable list view logging
            # ... other admin configurations ...
        ```
    """

    # To write audit log of each instance in the admin view
    write_accessed_from_list_view = False

    def changelist_view(self, request, extra_context=None):
        """
        Handles the changelist view (list view) and logs access events for
        objects on the current page if `write_accessed_from_list_view` is `True`.

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
        if self.write_accessed_from_list_view:
            changelist = response.context_data["cl"]
            for obj in changelist.result_list:
                accessed.send(sender=obj.__class__, instance=obj, actor=request.user)
        return response

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        Logs the access event when the change view of an object is accessed.

        Args:
            request: The HTTP request object.
            object_id: The ID of the object being changed.
            form_url: The URL of the change form.
            extra_context: Optional extra context to pass to the template.

        Returns:
            The response from the superclass's `change_view` method.
        """
        obj = self.get_object(request, object_id)
        if obj is not None:
            accessed.send(sender=obj.__class__, instance=obj, actor=request.user)
        return super().change_view(request, object_id, form_url, extra_context)

    def history_view(self, request, object_id, extra_context=None):
        """
        Logs the access event when the history view of an object is accessed.

        Args:
            request: The HTTP request object.
            object_id: The ID of the object whose history is being viewed.
            extra_context: Optional extra context to pass to the template.

        Returns:
            The response from the superclass's `history_view` method.
        """
        obj = self.get_object(request, object_id)
        if obj is not None:
            accessed.send(sender=obj.__class__, instance=obj, actor=request.user)
        return super().history_view(request, object_id, extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        """
        Logs the access event when the delete view of an object is accessed.

        Args:
            request: The HTTP request object.
            object_id: The ID of the object being deleted.
            extra_context: Optional extra context to pass to the template.

        Returns:
            The response from the superclass's `delete_view` method.
        """
        obj = self.get_object(request, object_id)
        if obj is not None:
            accessed.send(sender=obj.__class__, instance=obj, actor=request.user)
        return super().delete_view(request, object_id, extra_context)

# Django Auditlog Extra

A module that fixes some issues and provides some reusable tools for Django application using `django-auditlog` in the context of **City of Helsinki**, that uses **Django Auditlog with Django Graphene** or Django Rest Framework.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Context](#context)
  - [Django Auditlog](#django-auditlog)
  - [Django Graphene](#django-graphene)
  - [Django Rest Framework](#django-rest-framework)
- [FAQ](#faq)
- [Installation](#installation)
- [Features](#features)
  - [Context manager](#context-manager)
    - [`set_request_path`](#set_request_path)
  - [Middleware](#middleware)
    - [`AuditlogMiddleware`](#auditlogmiddleware)
  - [Graphene Decorators](#graphene-decorators)
    - [`auditlog_access`](#auditlog_access)
  - [Mixins](#mixins)
    - [`AuditlogAdminViewAccessLogMixin`](#auditlogadminviewaccesslogmixin)
  - [Utilities](#utilities)
    - [`AuditLogConfigurationHelper`](#auditlogconfigurationhelper)
      - [Initialization examples for `AuditLogConfigurationHelper`:](#initialization-examples-for-auditlogconfigurationhelper)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Context

### Django Auditlog

> PyPi: https://pypi.org/project/django-auditlog/.
>
> Github: https://github.com/jazzband/django-auditlog.
>
> Docs: https://django-auditlog.readthedocs.io/en/latest/index.html.

The `Django-auditlog` is a reusable app for Django that makes logging changes to your models a breeze. It provides a simple and efficient way to track who made changes to your data and when. This is crucial for accountability, debugging, and compliance with regulations like GDPR.

> NOTE: The `django-auditlog` is supported by the **Platta structured log transfer utility** (https://github.com/City-of-Helsinki/structured-log-transfer).

Here's a breakdown of what it offers:

- **Automatic Change Logging**: It automatically logs changes to your Django models, including creation, updates, and deletion. You can easily track who made the changes and what those changes were.

- **Customization**: You can customize which fields to track, the logging level (e.g., only log changes to specific fields), and even use signals to trigger actions based on logged events.

- **Integration with Existing Models**: It seamlessly integrates with your existing Django models. You can easily add audit logging to new or existing models with minimal code changes.

- **Simple Setup**: It's easy to install and configure. You can get started quickly with just a few lines of code.

- **Performance** : Django-auditlog is designed to be fast and efficient, minimizing the performance impact on your application.

Here's why you might use `django-auditlog`:

- **Debugging**: Easily identify the cause of data inconsistencies by reviewing the history of changes.

- **Security and Compliance**: Track user actions to meet regulatory requirements and identify potentially malicious activity.

- **Data Analysis**: Gain insights into how your data is being used and modified over time.

- **Accountability**: Ensure that users are held accountable for their actions within your application.

If you're building a Django application where tracking data changes is important, django-auditlog is a valuable tool to consider.

### Django Graphene

> PyPi: https://pypi.org/project/graphene-django/.
>
> Github: https://github.com/graphql-python/graphene-django.
>
> Docs: https://docs.graphene-python.org/projects/django/en/latest/.

Django Graphene is a library that integrates the Django web framework with Graphene, a Python library for building GraphQL APIs. It allows you to easily create GraphQL APIs in your Django projects, leveraging the power and flexibility of GraphQL while maintaining the simplicity and structure of Django.

### Django Rest Framework

> PyPi: https://pypi.org/project/djangorestframework/.
>
> Github: https://github.com/encode/django-rest-framework.
>
> Docs: https://www.django-rest-framework.org/.

Django REST framework is a powerful and flexible toolkit that makes it easier to build Web APIs using the Django framework.

## FAQ

There have been some incompatibility issues with `django-auditlog` and `django-graphene`. Some solutions to that and answers to some other common questions, issues and more details, see the [FAQ.md](./docs/FAQ.md).

## Installation

**Dependencies (TODO):**
For actor handling, django-auditlog and test usage:

- **`django.contrib.auth`**: Django built-in
- **`django.contrib.contenttypes`**: Django built-in
- **`auditlog`**: django-auditlog

**`settings.py`**:

```python
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "auditlog",
    # ...
    "hel_django_auditlog_extra.apps.HelDjangoAuditLogExtraConfig",
```

## Features

### Context manager

Code reference: [context.py](./context.py).

#### `set_request_path`

    Store the request path in the LogEntry's `additional_data` field.

    This context manager uses a ContextVar to store the request path and
    connects a signal receiver to automatically add it to LogEntry instances.
    It uses a unique signal_duid to prevent duplicate signals when nested.

NOTE: This is used by the [`AuditlogMiddleware`](#middleware).

### Middleware

Code reference: [middleware.py](./middleware.py).

#### `AuditlogMiddleware`

    Extends the `auditlog.middleware.AuditlogMiddleware` to fix an issue
    with setting the actor in the audit log context.

    This middleware extends the `auditlog.middleware.AuditlogMiddleware` to
    address a potential issue where the actor (user and their IP address)
    might not be available when `auditlog` attempts to access it.

    It achieves this by explicitly setting the actor in the
    audit log context before the request is processed. This ensures that
    audit logs accurately reflect the user responsible for each action.

    This fix is based on the suggestion provided in:
    https://github.com/jazzband/django-auditlog/issues/115#issuecomment-1682234986

    Additionally, this middleware sets the request path in the audit log
    context, providing more context for each logged action.

To use, add `"hel_django_auditlog_extra.middleware.AuditlogMiddleware"` to the list of the middlewares in `settings.py`, (instead of the one that `django-auditlog` offers):

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # ...other middlewares that manipulates request context...
    "hel_django_auditlog_extra.middleware.AuditlogMiddleware",
]
```

### Graphene Decorators

Code reference: [graphene_decorators.py](./graphene_decorators.py).

#### `auditlog_access`

    Decorator to init audit logging to a Graphene DjangoObjectType's get_node method.

    Uses the `accessed` signal to log the access of the node.

To use this decorator for a GraphQL Node, add it to the Node-class that is implementing a `DjangoObjectType`. The decorator will then wrap the `get_node` -function, that is inherited from the `DjangoObjectType`.

```python
@auditlog_access
class ChildNode(DjangoObjectType):

    # fields...

    class Meta:
        model = Child
        # meta...

    # methods...
    @classmethod
    @login_required
    def get_node(cls, info, id):
        try:
            return cls._meta.model.objects.user_can_view(info.context.user).get(id=id)
        except cls._meta.model.DoesNotExist:
            return None
```

### Mixins

Code reference: [mixins.py](./mixins.py).

#### `AuditlogAdminViewAccessLogMixin`

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

### Utilities

Code reference: [utils.py](./utils.py).

#### `AuditLogConfigurationHelper`

    A helper class for managing audit log configuration in your Django project.

    This class provides methods to:

    - Retrieve all models in your project.
    - Identify models that are not explicitly configured for audit logging.
    - Raise an error if any models are not configured when
    `AUDITLOG_INCLUDE_ALL_MODELS` is enabled.

    This helps ensure that all models are either explicitly included or excluded
    from audit logging, preventing accidental omissions.

NOTE: The `AuditLogConfigurationHelper` can be used only after all the apps are ready.

Example usage: Use when the audit log registry is already configured...

```python
AuditLogConfigurationHelper.raise_error_if_unconfigured_models()
```

##### Initialization examples for `AuditLogConfigurationHelper`:

- One place to call this helper function would be in the ready-function of the last app's configuration, when all the models are already registered. You can even add an `apps.py` file into your main Django project folder and then add the project app to the list of the `INSTALLED_APPS` in project's `settings.py`. The important thing is that it should be the last one with models.

  **`apps.py`**:

  ```python
  from django.apps import AppConfig

  class MainProjectConfig(AppConfig):
      name = "mainproject"

      def ready(self):
          from hel_django_auditlog_extra.utils import AuditLogConfigurationHelper

          AuditLogConfigurationHelper.raise_error_if_unconfigured_models()
  ```

  **`settings.py`**:

  ```python
  INSTALLED_APPS = [
      "django.contrib.auth",
      "django.contrib.contenttypes",
      "django.contrib.sessions",
      "django.contrib.messages",
      "django.contrib.staticfiles",
      "auditlog",
      # local apps
      "events",
      "hel_django_auditlog_extra.apps.HelDjangoAuditLogExtraConfig",
      "mainproject",
      "django_cleanup.apps.CleanupConfig",  # This must be included last
  ]
  ```

- Another way to achieve this would be using a `post_migrate` signal receiver, which is called after the migration process (`python manage.py migrate`) is done:

  **`signals.py`**:

  ```python
  from django.apps import apps
  from django.db.models.signals import post_migrate
  from django.dispatch import receiver

  from hel_django_auditlog_extra.utils import AuditLogConfigurationHelper


  @receiver(post_migrate)
  def check_audit_log_configuration(sender, **kwargs):
      """
      Signal receiver to check audit log configuration after all apps are migrated.
      """
      if apps.ready:
          AuditLogConfigurationHelper.raise_error_if_unconfigured_models()
  ```

  Remember that signals and receivers needs to be connected (for example in `apps.py`):

  ```python
  from django.apps import AppConfig
  from django.core.signals import request_finished


  class MyAppConfig(AppConfig):
      ...

      def ready(self):
          # Implicitly connect signal handlers decorated with @receiver.
          from . import signals

          # Explicitly connect a signal handler.
          request_finished.connect(signals.my_callback)
  ```

  Reference: https://docs.djangoproject.com/en/5.1/topics/signals/#listening-to-signals.

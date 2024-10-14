# Kukkuu

:baby: Culture Kids (kulttuurin kummilapset) API :violin:

[![status](https://travis-ci.com/City-of-Helsinki/kukkuu.svg)](https://github.com/City-of-Helsinki/kukkuu)

## Environments

Production environment:

- https://kukkuu-api.prod.hel.ninja/kukkuu/graphql

Testing environment:

- https://kukkuu.api.test.hel.ninja/graphql

## Development with Docker

1. Copy `docker-compose.env.yaml.example` to `docker-compose.env.yaml` and modify it if needed.

2. Run `docker compose up`

If you do not have a super user / admin to administrate the API yet, you can create one with `docker compose run django python manage.py add_admin_user -u admin -p admin -e admin@example.com`.

The project is now running at [localhost:8081](http://localhost:8081)

## Development without Docker

Prerequisites:

- PostgreSQL 12
- Python 3.11

### Installing Python requirements

- Run `pip install -r requirements.txt`
- Run `pip install -r requirements-dev.txt` (development requirements)

### Database

To setup a database compatible with default database settings:

Create user and database

    sudo -u postgres createuser -P -R -S kukkuu  # use password `kukkuu`
    sudo -u postgres createdb -O kukkuu kukkuu

Allow user to create test database

    sudo -u postgres psql -c "ALTER USER kukkuu CREATEDB;"

Add default languages (optional)

    python manage.py add_languages --default

**NOTE:** A few of the default languages may not have a properly translated name in all languages.

Add admin user (optional)

    python manage.py add_admin_user -u admin -p admin -e admin@example.com

### Notification import

The emails notifications that Kukkuu sends can be imported from a Google Sheets spreadsheet. To do that, first configure setting `KUKKUU_NOTIFICATIONS_SHEET_ID`, and then either

1. run `python manage.py import_notifications` to import and update all the notifications, or
2. use actions in Django admin UI's notification list view to have finer control on which notifications to update and create

### Cron jobs

`cron` is required for sending reminder notifications, and for sending emails queued (optional).

#### Reminder notifications

To send reminder notifications on time, `send_reminder_notifications` management command needs to be executed (at least) daily.

Example crontab for sending reminder notifications every day at 12am:

    0 12 * * * (/path/to/your/python path/to/your/app/manage.py send_reminder_notifications > /var/log/cron.log 2>&1)
    # An empty line is required at the end of this file for a valid cron file.

#### Feedback notifications

To send notifications asking for feedback of recently ended events occurrences, `send_feedback_notifications` management command needs to be executed periodically.

An additional delay between an occurrence's end time and the notification's send time can be configured with setting `KUKKUU_FEEDBACK_NOTIFICATION_DELAY`. The default value is `15`(min).

Example crontab for sending feedback notifications:

    1,16,31,46 * * * * (/path/to/your/python path/to/your/app/manage.py send_reminder_notifications > /var/log/cron.log 2>&1)
    # An empty line is required at the end of this file for a valid cron file.

#### Queued email sending

By default email sending is queued, which means that you need to set `send_mail` and `retry_deferred` to be executed periodically to get emails actually sent.

Example crontab for queued emails (includes reminder notification sending as well):

    * * * * * (/path/to/your/python path/to/your/app/manage.py send_mail > /var/log/cron.log 2>&1)
    0,20,40 * * * * (/path/to/your/python path/to/your/app/manage.py retry_deferred > /var/log/cron.log 2>&1)
    0 0 * * * (/path/to/your/python path/to/your/app/manage.py purge_mail_log 7 > /var/log/cron.log 2>&1)
    0 12 * * * (/path/to/your/python path/to/your/app/manage.py send_reminder_notifications > /var/log/cron.log 2>&1)
    # An empty line is required at the end of this file for a valid cron file.

It is also possible to get emails sent right away without any cronjobs by setting `ILMOITIN_QUEUE_NOTIFICATIONS` to `False`, which can be convenient in development. **CAUTION** do not use this in production!

#### SMS notifications

To use the SMS notification functionality, you have to acquire the API_KEY from [Notification Service API](https://github.com/City-of-Helsinki/notification-service-api). The following environment variables are needed:

        ```python
        NOTIFICATION_SERVICE_API_TOKEN=your_api_key
        NOTIFICATION_SERVICE_API_URL=notification_service_end_point
        ```

### Daily running, Debugging

- Create `.env` file: `touch .env`
- Set the `DEBUG` environment variable to `1`.
- Run `python manage.py migrate`
- Run `python manage.py runserver localhost:8081`
- The project is now running at [localhost:8081](http://localhost:8081)

## Authorization

The user profiles authenticates themselves in a centralized authentication server of the city of Helsinki. For long it has been [Tunnistamo](https://github.com/City-of-Helsinki/tunnistamo), but in the summer of the year 2024, it should be changed to a Keycloak service of the [Helsinki-Profile](https://github.com/City-of-Helsinki/open-city-profile) service environment.

The Tunnistamo can be configured to be used [locally](./docs/setup-tunnistamo.md#use-a-local-tunnistamo) or from the [test environment](./docs/setup-tunnistamo.md#use-the-public-test-tunnistamo).

The Keycloak test environment can also be configured to be used [locally](./docs/setup-keycloak.md).

> NOTE: Also check the [GDPR API documentation](./gdpr/README.md) because there is much more detailed instructions how to setup the Tunnistamo and the Helsinki-Profile!

## GDPR API data export

The [GDPR API data export and API tester documentation](./gdpr/README.MD).

## GraphQL API Documentation

To view the GraphQL API documentation, in DEBUG mode visit: http://localhost:8081/graphql and checkout the `Documentation Explorer` section

## Report API

For fetching data for reporting purposes there is a separate REST API located at [localhost:8081/reports/](http://localhost:8081/reports/).

The API requires authentication via HTTP basic authentication, or alternatively session authentication when DEBUG is `True`. The accessing user must also have Django permission `reports.access_report_api`.

API documentation of the report API can be viewed at [localhost:8081/reports/schema/redoc/](http://localhost:8081/reports/schema/redoc/).

## QR-code ticket verification

When an enrolment is created, the guardian has get a mail in a text format. This pull request adds a QR-code to the mail's attachments. The QR-code is created from the ticket verification url and the enrolment's reference id, which is 5 chars code (lowercased alphabets) that is easy to write manually in the urls if needed.

If KUKKUU_TICKET_VERIFICATION_URL is set to None, the QR-code won't be attached to the enrolment notification email. Use {reference_id} as a specified value in the given string, e.g http://localhost:3000/check-ticket-validity/{reference_id}.

The [Hashids](https://hashids.org/python/) is used to create the magic number that is used as a reference id to Enrolment instance. A salt is needed to prevent the malicious users to guess the magic numbers to tickets.

```
KUKKUU_HASHID_SALT=ULGd5YeRv6yVtvoj
KUKKUU_TICKET_VERIFICATION_URL=http://localhost:3000/check-ticket-validity/{reference_id}
```

## Keeping Python requirements up to date

1. Install `pip-tools`:

   - `pip install pip-tools`

2. Add new packages to `requirements.in` or `requirements-dev.in`

3. Update `.txt` file for the changed requirements file:

   - `pip-compile requirements.in`
   - `pip-compile requirements-dev.in`

4. If you want to update dependencies to their newest versions, run:

   - `pip-compile --upgrade requirements.in`

5. To install Python requirements run:

   - `pip-sync requirements.txt`

### Forked Django Application: Django-Ilmoitin

There is a fork of the `django-ilmoitin` Django application [(link to original repo)](https://github.com/City-of-Helsinki/django-ilmoitin) in this project.

**Reason for Forking:**

The official version of `django-ilmoitin` does not currently properly support Django 4.x, since there are some migrations that needs to be applied in the official version still. This fork has been modified to ensure compatibility.

**Key Modifications:**

- Auto generated migrations (with `python manage.py makemigrations`) in [django_ilmoitin/migrations/0006_alter_notificationtemplate_admins_to_notify_and_more.py](./django_ilmoitin/migrations/0006_alter_notificationtemplate_admins_to_notify_and_more.py)
  ```
  Migrations for 'django_ilmoitin':
  django_ilmoitin/migrations/0006_alter_notificationtemplate_admins_to_notify_and_more.py
  - Alter field admins_to_notify on notificationtemplate
  - Alter field id on notificationtemplatetranslation
  ```

**Updating to the Official Version:**

Once `django-ilmoitin` officially supports Django 4.2, this fork can be replaced. To update:

1. remove this fork by removing the `django-ilmoitin` directory in [./django-ilmoitin](./django_ilmoitin/).
2. install the official package update by updating the `django-ilmoitin` in [requirements.txt](./requirements.txt). While the `pip-tools` are in use, the upgrade can be done with the `pip-compile` updgrade command:

```
pip-compile -P django-ilmoitin requirements.in
```

To update the file in your own local Python virtualenv, use `pip-sync`:

```
pip-sync requirements.txt requirements-dev.txt
```

3. handle the migrations. Compare the migrations that have been applied in [django_ilmoitin/migrations/0006_alter_notificationtemplate_admins_to_notify_and_more.py](./django_ilmoitin/migrations/0006_alter_notificationtemplate_admins_to_notify_and_more.py) with the ones that now comes from the updated 3rd party package. Some faking may be needed. See more https://docs.djangoproject.com/en/4.2/ref/django-admin/#cmdoption-migrate-fake.

## Code linting & formatting

This project uses [ruff](https://github.com/astral-sh/ruff) for Python code linting and formatting.
Ruff is configured through [pyproject.toml](./pyproject.toml).
Basic `ruff` commands:

- Check linting: `ruff check` or `ruff check --fix` to auto-fix
- Check & auto-fix linting: `ruff check --fix`
- Format: `ruff format`

Basically:

- Ruff linter (i.e. `ruff check --fix`) does what `flake8` and `isort` did before.
- Ruff formatter (i.e. `ruff format`) does what `black` did before.

Integrations for `ruff` are available for many editors:

- https://docs.astral.sh/ruff/integrations/

### Pre-commit hooks

You can use [`pre-commit`](https://pre-commit.com/) to lint and format your code before committing:

1. Install `pre-commit` (there are many ways to do but let's use pip as an example):
   - `pip install pre-commit`
2. Set up git hooks from `.pre-commit-config.yaml`, run this command from project root:
   - `pre-commit install`

After that, linting and formatting hooks will run against all changed files before committing.

## Issues board

https://helsinkisolutionoffice.atlassian.net/projects/KK/issues/?filter=allissues

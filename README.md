# Kukkuu API documentation

:baby: The Culture Kids (Kulttuurin kummilapset) API :violin:

[![status](https://travis-ci.com/City-of-Helsinki/kukkuu.svg)](https://github.com/City-of-Helsinki/kukkuu)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Service architecture](#service-architecture)
  - [Environments](#environments)
- [Development](#development)
  - [Development with Docker](#development-with-docker)
  - [Development without Docker](#development-without-docker)
    - [Installing Python requirements](#installing-python-requirements)
    - [Database](#database)
    - [Notification import](#notification-import)
  - [Daily running, Debugging](#daily-running-debugging)
- [Authorization](#authorization)
- [Cron jobs](#cron-jobs)
  - [Reminder notifications](#reminder-notifications)
  - [Feedback notifications](#feedback-notifications)
  - [Queued email sending](#queued-email-sending)
  - [SMS notifications](#sms-notifications)
- [Application programming interfaces](#application-programming-interfaces)
  - [GraphQL API Documentation](#graphql-api-documentation)
  - [Report API](#report-api)
  - [GDPR API data export](#gdpr-api-data-export)
- [Event Ticketing](#event-ticketing)
  - [Internal Ticketing](#internal-ticketing)
  - [External Ticketing](#external-ticketing)
- [Audit logging](#audit-logging)
- [Keeping Python requirements up to date](#keeping-python-requirements-up-to-date)
- [Code linting & formatting](#code-linting--formatting)
  - [Pre-commit hooks](#pre-commit-hooks)
- [Issues board](#issues-board)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Service architecture

The Culture kids service consists from:

- **Kukkuu API:** The (this) backend service. 
- **[Public UI](https://github.com/City-of-Helsinki/kukkuu-ui):** The frontend service where the kids can view and enrol to culture events.
- **[Admin UI](https://github.com/City-of-Helsinki/kukkuu-admin):** A restricted UI where the events are maintained and published.
- **[Headless CMS](https://github.com/City-of-Helsinki/headless-cms):** Content Management Service that provides dynamic pages and dynamic content for the public UI. It also provides content for the header and the footer. A React component library can be found from https://github.com/City-of-Helsinki/react-helsinki-headless-cms.
- **[Notification Service API](https://github.com/City-of-Helsinki/notification-service-api):** A service used by the Kukkuu API to send SMS messages.
- **Mailer:** A service used by the Kukkuu API to send emails.

### Environments

The API environments:
- **Production environment:** https://kukkuu.api.hel.fi/graphql
- **Staging environment:** https://kukkuu.api.stage.hel.ninja/graphql
- **Testing environment:** https://kukkuu.api.test.hel.ninja/graphql

The public client environments:
- **Production environment:** https://kummilapset.hel.fi/
- **Staging environment:** https://kukkuu-ui.stage.hel.ninja/
- **Testing environment:** https://kukkuu-ui.test.hel.ninja/

The admin client environments:
- **Production environment:** https://kummilapset-admin.hel.fi/
- **Staging environment:** https://kukkuu-admin.stage.hel.ninja/
- **Testing environment:** https://kukkuu-admin.test.hel.ninja/

The headless CMS environments:
- **Production environment:** https://kukkuu.content.api.hel.fi/graphql
- **Testing environment:** https://kukkuu.app-staging.hkih.hion.dev/graphql

The notification service environments: 
- **Production environment:** https://kuva-notification-service.api.hel.fi/
- **Staging environment:** https://kuva-notification-service.api.stage.hel.ninja/
- **Testing environment:** https://kuva-notification-service.api.test.hel.ninja/

## Development

### Development with Docker

1. Copy `docker-compose.env.yaml.example` to `docker-compose.env.yaml` and modify it if needed.

2. Run `docker compose up`

If you do not have a super user / admin to administrate the API yet, you can create one with `docker compose run django python manage.py add_admin_user -u admin -p admin -e admin@example.com`.

The project is now running at [localhost:8081](http://localhost:8081)

### Development without Docker

Prerequisites:

- PostgreSQL 13
- Python 3.11

#### Installing Python requirements

- Run `pip install -r requirements.txt`
- Run `pip install -r requirements-dev.txt` (development requirements)

#### Database

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

#### Notification import

The emails notifications that Kukkuu sends can be imported from a Google Sheets spreadsheet. To do that, first configure setting `KUKKUU_NOTIFICATIONS_SHEET_ID`, and then either

1. run `python manage.py import_notifications` to import and update all the notifications, or
2. use actions in Django admin UI's notification list view to have finer control on which notifications to update and create

### Daily running, Debugging

- Create `.env` file: `touch .env`
- Set the `DEBUG` environment variable to `1`.
- Run `python manage.py migrate`
- Run `python manage.py runserver localhost:8081`
- The project is now running at [localhost:8081](http://localhost:8081)

## Authorization

Kukkuu uses Keycloak, an open-source identity and access management solution, for user authentication and authorization. Keycloak is integrated with the Helsinki-Profile service environment.

**Keycloak Setup:**

*   **Local Development:** You can configure Keycloak for local development by following the instructions in [this guide](./docs/setup-keycloak.md). This allows you to test authentication flows without relying on external services.


**Browser Testing and Authorization:**

Protecting sensitive data while enabling effective browser testing requires a secure authorization process. To avoid the limitations of mocking responses, Kukkuu utilizes symmetrically signed JWTs (JSON Web Tokens) specifically for browser testing.

> The symmetrically signed JWT means that both ends, the client and the API both needs to share a shared secret between each other, that can be used to sign the JWT. Also, the API needs to be configured so that it allows JWT issued by the client (and not the actual authorization service).

**How it works:**

1.  **Shared Secret:**  The client (browser) and the Kukkuu API share a secret key.
2.  **JWT Signing:** The client uses the shared secret to sign a JWT, effectively asserting its identity for testing purposes.
3.  **API Configuration:** The API is configured to trust JWTs signed with the shared secret, bypassing the standard Keycloak authentication flow for browser testing.

This approach allows for realistic browser testing while safeguarding sensitive data.

**Important Notes:**

*   Ensure the shared secret used for browser testing is kept secure and separate from production secrets.
*   For production environments, Kukkuu relies on standard Keycloak authentication flows through the Helsinki-Profile.


**Further Information:**

*   For detailed instructions on setting up Tunnistamo (the previous authentication system) and Helsinki-Profile, refer to the [GDPR API documentation](./gdpr/README.md).

## Cron jobs

`cron` is required for sending reminder notifications, and for sending emails queued (optional).

### Reminder notifications

To send reminder notifications on time, `send_reminder_notifications` management command needs to be executed (at least) daily.

Example crontab for sending reminder notifications every day at 12am:

    0 12 * * * (/path/to/your/python path/to/your/app/manage.py send_reminder_notifications > /var/log/cron.log 2>&1)
    # An empty line is required at the end of this file for a valid cron file.

### Feedback notifications

To send notifications asking for feedback of recently ended events occurrences, `send_feedback_notifications` management command needs to be executed periodically.

An additional delay between an occurrence's end time and the notification's send time can be configured with setting `KUKKUU_FEEDBACK_NOTIFICATION_DELAY`. The default value is `15`(min).

Example crontab for sending feedback notifications:

    1,16,31,46 * * * * (/path/to/your/python path/to/your/app/manage.py send_reminder_notifications > /var/log/cron.log 2>&1)
    # An empty line is required at the end of this file for a valid cron file.

### Queued email sending

By default email sending is queued, which means that you need to set `send_mail` and `retry_deferred` to be executed periodically to get emails actually sent.

Example crontab for queued emails (includes reminder notification sending as well):

    * * * * * (/path/to/your/python path/to/your/app/manage.py send_mail > /var/log/cron.log 2>&1)
    0,20,40 * * * * (/path/to/your/python path/to/your/app/manage.py retry_deferred > /var/log/cron.log 2>&1)
    0 0 * * * (/path/to/your/python path/to/your/app/manage.py purge_mail_log 7 > /var/log/cron.log 2>&1)
    0 12 * * * (/path/to/your/python path/to/your/app/manage.py send_reminder_notifications > /var/log/cron.log 2>&1)
    # An empty line is required at the end of this file for a valid cron file.

It is also possible to get emails sent right away without any cronjobs by setting `ILMOITIN_QUEUE_NOTIFICATIONS` to `False`, which can be convenient in development. **CAUTION** do not use this in production!

### SMS notifications

To use the SMS notification functionality, you have to acquire the API_KEY from [Notification Service API](https://github.com/City-of-Helsinki/notification-service-api). The following environment variables are needed:

        ```python
        NOTIFICATION_SERVICE_API_TOKEN=your_api_key
        NOTIFICATION_SERVICE_API_URL=notification_service_end_point
        ```

## Application programming interfaces

### GraphQL API Documentation

The primary API to fetch Kukkuu related data is a GraphQL API created with Graphene. To view the GraphQL API documentation, in DEBUG mode visit: http://localhost:8081/graphql and checkout the `Documentation Explorer` section.

### Report API

For fetching data for reporting purposes, there is a separate REST API located at [localhost:8081/reports/](http://localhost:8081/reports/). Unlike the primary API which is created with Graphene, the Report API is created with Django REST Framework.

The API requires authentication via HTTP basic authentication, or alternatively session authentication when DEBUG is `True`. The accessing user must also have Django permission `reports.access_report_api`.

API documentation of the report API can be viewed at [localhost:8081/reports/schema/redoc/](http://localhost:8081/reports/schema/redoc/).


### GDPR API data export

The [GDPR API data export and API tester documentation](./gdpr/README.MD).


## Event Ticketing

Kukkuu handles event ticketing in two ways: **internal** and **external**. This allows flexibility for managing different types of events and integrating with existing ticketing systems.

A child is always associated with a specific "year project" based on their birth year. Events are also linked to these year projects.  Typically, a child can attend 2-3 events per calendar year, but this can be configured per project.

### Internal Ticketing

For events managed internally, Kukkuu provides the following features:

* **Enrolment Management:**  
    * Enrolments are handled directly through the Kukkuu API and can be managed using the Kukkuu Admin UI.
    * Each enrolment creates an `Enrolment` model instance in the database, storing all relevant contact information.
* **GraphQL API Access:** Project admins can fetch enrolment data for their events via the GraphQL API.  Admins have access only to events within their assigned projects.
* **QR Code Ticket Verification:**
    * Enrolment confirmation emails include a QR code for easy ticket verification.
    * This QR code links to a verification URL (configurable via `KUKKUU_TICKET_VERIFICATION_URL`) and includes a unique reference ID generated using `Hashids` (with a salt defined in `KUKKUU_HASHID_SALT`).

    ```
    KUKKUU_HASHID_SALT=your_secret_salt
    KUKKUU_TICKET_VERIFICATION_URL=http://your-verification-domain/check-ticket-validity/{reference_id}
    ```

### External Ticketing

Kukkuu integrates with the following external ticketing systems:

* Ticketmaster
* Lippu.fi
* Tixly

When an event uses an external ticketing system:

* **Coupon-Based Enrolment:** Kukkuu provides pre-stored coupon codes that can be used to "purchase" tickets through the external system.
* **No Internal Enrolment:** Instead of creating an `Enrolment` instance, Kukkuu links a coupon code to the child when they are enrolled in an externally ticketed event.
* **Ticket Management:**  Enrolment details are managed within the external ticketing system, not within Kukkuu.

**Managing Coupon Codes:**

Coupon codes for external ticketing systems can be added through the Kukkuu Admin UI or the API. These codes are stored as `TicketSystemPassword` model instances.


## Audit logging

Audit logging is implemented with `django-auditlog`, but it has some extended features applied with [hel_django_auditlog_extra](./hel_django_auditlog_extra/) -app. To see documentation related to that, read it's [README](./hel_django_auditlog_extra/README.md) and [FAQ](./hel_django_auditlog_extra/docs/FAQ.md).

The configuration to define which models are in the scope of the audit logging can be found from [auditlog_settings.py](./kukkuu/auditlog_settings.py).

The GraphQL and admin site views can be logged by using the mixins and decorators that the `hel_django_auditlog_extra` provides (see: [README](./hel_django_auditlog_extra/README.md#features)).

**References**:

- Django-auditlog

  > PyPi: https://pypi.org/project/django-auditlog/.
  >
  > Github: https://github.com/jazzband/django-auditlog.
  >
  > Docs: https://django-auditlog.readthedocs.io/en/latest/index.html.

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
   - `pre-commit install` for code formatting & linting
   - `pre-commit install --hook-type commit-msg` for commit message linting

After that, linting and formatting hooks will run against all changed files before committing.

Git commit message linting is configured in [.gitlint](./.gitlint)

## Issues board

https://helsinkisolutionoffice.atlassian.net/projects/KK/issues/?filter=allissues

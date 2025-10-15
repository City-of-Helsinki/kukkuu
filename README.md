# Kukkuu API documentation

:baby: The Culture Kids (Kulttuurin kummilapset) API :violin:

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Service architecture](#service-architecture)
  - [Environments](#environments)
- [Development](#development)
  - [Requirements](#requirements)
  - [Development with Docker](#development-with-docker)
  - [Development without Docker](#development-without-docker)
    - [Installing Python requirements](#installing-python-requirements)
    - [Database](#database)
    - [Notification import](#notification-import)
    - [Daily running, Debugging](#daily-running-debugging)
  - [Generating secret key for Django](#generating-secret-key-for-django)
  - [Getting secret for django-admin login](#getting-secret-for-django-admin-login)
  - [Keeping Python requirements up to date](#keeping-python-requirements-up-to-date)
  - [Code format](#code-format)
  - [Commit message format](#commit-message-format)
- [Application programming interfaces](#application-programming-interfaces)
  - [GraphQL API Documentation](#graphql-api-documentation)
  - [Report API](#report-api)
  - [GDPR API data export](#gdpr-api-data-export)
- [Event Ticketing](#event-ticketing)
  - [Internal Ticketing](#internal-ticketing)
  - [External Ticketing](#external-ticketing)
- [Authorization](#authorization)
- [Audit logging](#audit-logging)
- [Cron jobs](#cron-jobs)
  - [Reminder notifications](#reminder-notifications)
  - [Feedback notifications](#feedback-notifications)
  - [Queued email sending](#queued-email-sending)
  - [SMS notifications](#sms-notifications)
- [Releases, changelogs and deployments](#releases-changelogs-and-deployments)
  - [Conventional Commits](#conventional-commits)
  - [Releasable units](#releasable-units)
  - [Configuration](#configuration)
  - [Troubleshoting release-please](#troubleshoting-release-please)
    - [Fix merge conflicts by running release-please -action manually](#fix-merge-conflicts-by-running-release-please--action-manually)
  - [Deployments](#deployments)
- [Issues board](#issues-board)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Service architecture

The Culture kids service consists from:

- **[Kukkuu API](https://github.com/City-of-Helsinki/kukkuu):** The (this) backend service.
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

### Requirements

Compatibility defined by [Dockerfile](./Dockerfile) and [compose.yaml](./compose.yaml):

- PostgreSQL 17
- Python 3.12

Optionally if you want to use pre-commit hooks:

- Node.js 20 for using pre-commit hook's `doctoc`
  - Has been tested with Node.js 20, might work with other versions too

### Development with Docker

1. Copy `.env.example` to `.env`
2. Set value for `SECRET_KEY` to `.env` with [Generating secret key for Django](#generating-secret-key-for-django) instructions
3. Set value for `SOCIAL_AUTH_TUNNISTAMO_SECRET` to `.env` with [Getting secret for django admin login](#getting-secret-for-django-admin-login) instructions
4. Run `docker compose up`

If you do not have a super user / admin to administrate the API yet, you can create one with:

- `docker exec -it kukkuu-backend python manage.py add_admin_user -u admin -p admin -e admin@example.com`
  - In case you have running container already
- `docker compose run django python manage.py add_admin_user -u admin -p admin -e admin@example.com`
  - In case you don't have a running container yet

The project is now running at http://localhost:8081 and using public Keycloak test environment for authentication.

### Development without Docker

1. Install [requirements](#requirements)
2. Copy `.env.example` to `.env`
3. Set value for `SECRET_KEY` to `.env` with [Generating secret key for Django](#generating-secret-key-for-django) instructions
4. Set value for `SOCIAL_AUTH_TUNNISTAMO_SECRET` to `.env` with [Getting secret for django admin login](#getting-secret-for-django-admin-login) instructions
5. Modify `DATABASE_URL` and `DATABASE_HOST` in your `.env` file based on where your PostgreSQL database is set up

#### Installing Python requirements

- Run `pip install -r requirements.txt` (base requirements)
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

1. run `python manage.py import_notifications_from_google_sheets` to import and update all the notifications, or
2. use actions in Django admin UI's notification list view to have finer control on which notifications to update and create

The notification templates primary import source is https://docs.google.com/spreadsheets/d/1TkdQsO50DHOg5pi1JhzudOL1GKpiK-V2DCIoAipKj-M.

The environment variable should then be set to:

```
KUKKUU_NOTIFICATIONS_SHEET_ID=1TkdQsO50DHOg5pi1JhzudOL1GKpiK-V2DCIoAipKj-M
```

this is then set to `NOTIFICATIONS_SHEET_ID` in `settings.py`.

See more detailed instructions and other importer options from [notification_importers/README.md](./notification_importers/README.md).

#### Daily running, Debugging

- Create `.env` file: `touch .env`
- Set the `DEBUG` environment variable to `1`.
- Run `python manage.py migrate`
- Run `python manage.py runserver localhost:8081`
- The project is now running at http://localhost:8081

### Generating secret key for Django

Django needs a value for [SECRET_KEY](https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key) to start.

For production, you should use a strong, long, randomly generated key.

For local development, if you prefer, you can alternatively use a shorter, manually generated key.

Here's how you can generate a value for `SECRET_KEY` using Python (Based on Django v5.1.6's
[get_random_secret_key](https://github.com/django/django/blob/5.1.6/django/core/management/utils.py#L79C5-L84) &
[get_random_string](https://github.com/django/django/blob/5.1.6/django/utils/crypto.py#L51-L62)):

```python
import secrets, string
allowed_chars = string.ascii_lowercase + string.digits + "!@#$%^&*(-_=+)"
"".join(secrets.choice(allowed_chars) for i in range(50))
```

### Getting secret for django-admin login

To be able to log in to django-admin with Keycloak you need to set `SOCIAL_AUTH_TUNNISTAMO_SECRET`
in your environment—it is for Keycloak even though it's named Tunnistamo. Here's how you can get a
value for local development i.e. `kukkuu-django-admin-dev` client:

- Go to City of Helsinki's Azure DevOps [kukkuu project](https://dev.azure.com/City-of-Helsinki/kukkuu)
- Open `Pipelines > Library > development-kv` for the development keyvault library
- Read `Key vault name` value
- Open [Azure Portal](https://portal.azure.com/)
- Search Azure Portal with the key vault name you just read, and open the found key vault
- Open `Objects > Secrets`
- Find `SOCIAL-AUTH-TUNNISTAMO-SECRET` (may need pressing `Load more`), and open it
- Click on the hexadecimal current version value to open the secret's current version
- Click on the "Copy to clipboard" icon after the `Secret value` to copy it to clipboard
- Paste the value into your `.env` file as `SOCIAL_AUTH_TUNNISTAMO_SECRET=paste-the-copied-value-here`

### Keeping Python requirements up to date

If you're using Docker, spin up the container using `docker compose up`
and go into it with `docker exec -it kukkuu-backend bash` first.

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
   - Or if you're using Docker and the previous command fails:
     - Spin down the container with `docker compose down`
     - Rebuild the container with `docker compose up --build` to take the package changes into account

### Code format

This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and quality checking.

Basic `ruff` commands:

- lint: `ruff check`
- apply safe lint fixes: `ruff check --fix`
- check formatting: `ruff format --check`
- format: `ruff format`

[`pre-commit`](https://pre-commit.com/) can be used to install and
run all the formatting tools as git hooks automatically before a
commit.

### Commit message format

New commit messages must adhere to the [Conventional Commits](https://www.conventionalcommits.org/)
specification, and line length is limited to 72 characters.

When [`pre-commit`](https://pre-commit.com/) is in use, [`commitlint`](https://github.com/conventional-changelog/commitlint)
checks new commit messages for the correct format.

## Application programming interfaces

### GraphQL API Documentation

The primary API to fetch Kukkuu related data is a GraphQL API created with Graphene. To view the GraphQL API documentation, in DEBUG mode visit: http://localhost:8081/graphql and checkout the `Documentation Explorer` section.

### Report API

For fetching data for reporting purposes, there is a separate REST API located at http://localhost:8081/reports/. Unlike the primary API which is created with Graphene, the Report API is created with Django REST Framework.

The API requires authentication via HTTP basic authentication, or alternatively session authentication when DEBUG is `True`. The accessing user must also have Django permission `reports.access_report_api`.

API documentation of the report API can be viewed at http://localhost:8081/reports/schema/redoc/.

### GDPR API data export

The [GDPR API data export and API tester documentation](./gdpr/README.MD).

## Event Ticketing

Kukkuu handles event ticketing in two ways: **internal** and **external**. This allows flexibility for managing different types of events and integrating with existing ticketing systems.

A child is always associated with a specific "year project" based on their birth year. Events are also linked to these year projects. Typically, a child can attend 2-3 events per calendar year, but this can be configured per project.

### Internal Ticketing

For events managed internally, Kukkuu provides the following features:

- **Enrolment Management:**
  - Enrolments are handled directly through the Kukkuu API and can be managed using the Kukkuu Admin UI.
  - Each enrolment creates an `Enrolment` model instance in the database, storing all relevant contact information.
- **GraphQL API Access:** Project admins can fetch enrolment data for their events via the GraphQL API. Admins have access only to events within their assigned projects.
- **QR Code Ticket Verification:**

  - Enrolment confirmation emails include a QR code for easy ticket verification.
  - This QR code links to a verification URL (configurable via `KUKKUU_TICKET_VERIFICATION_URL`) and includes a unique reference ID generated using `Hashids` (with a salt defined in `KUKKUU_HASHID_SALT`).

  ```
  KUKKUU_HASHID_SALT=your_secret_salt
  KUKKUU_TICKET_VERIFICATION_URL=http://your-verification-domain/check-ticket-validity/{reference_id}
  ```

### External Ticketing

Kukkuu integrates with the following external ticketing systems:

- Ticketmaster
- Lippu.fi
- Tixly

When an event uses an external ticketing system:

- **Coupon-Based Enrolment:** Kukkuu provides pre-stored coupon codes that can be used to "purchase" tickets through the external system.
- **No Internal Enrolment:** Instead of creating an `Enrolment` instance, Kukkuu links a coupon code to the child when they are enrolled in an externally ticketed event.
- **Ticket Management:** Enrolment details are managed within the external ticketing system, not within Kukkuu.

**Managing Coupon Codes:**

Coupon codes for external ticketing systems can be added through the Kukkuu Admin UI or the API. These codes are stored as `TicketSystemPassword` model instances.

The easiest way to add multiple ticket system passwords (i.e. coupon codes) is to add them
using Kukkuu Admin UI. One needs to create/open an event, and
add coupon codes to it under tab "Salasanat" (i.e. passwords in Finnish)
with "Lisää salasanoja" (i.e. add passwords in Finnish). This interface
supports pasting a list of passwords as text, so mass adding is easy.

## Authorization

Kukkuu uses Keycloak, an open-source identity and access management solution, for user authentication and authorization. Keycloak is integrated with the Helsinki-Profile service environment.

**Keycloak Setup:**

- **Local Development:** You can configure Keycloak for local development by following the instructions in [this guide](./docs/setup-keycloak.md). This allows you to test authentication flows without relying on external services.

**Browser Testing and Authorization:**

Protecting sensitive data while enabling effective browser testing requires a secure authorization process. To avoid the limitations of mocking responses, Kukkuu utilizes symmetrically signed JWTs (JSON Web Tokens) specifically for browser testing.

> The symmetrically signed JWT means that both ends, the client and the API both
> need to share a shared secret between each other, that can be used to sign the JWT.
> Also, the API needs to be configured so that it allows JWT issued by the client
> (and not the actual authorization service).

**How it works:**

1.  **Shared Secret:** The client (browser) and the Kukkuu API share a secret key.
2.  **JWT Signing:** The client uses the shared secret to sign a JWT, effectively asserting its identity for testing purposes.
3.  **API Configuration:** The API is configured to trust JWTs signed with the shared secret, bypassing the standard Keycloak authentication flow for browser testing.

This approach allows for realistic browser testing while safeguarding sensitive data.

**Important Notes:**

- Ensure the shared secret used for browser testing is kept secure and separate from production secrets.
- For production environments, Kukkuu relies on standard Keycloak authentication flows through the Helsinki-Profile.

**Further Information:**

- For detailed instructions on setting up Tunnistamo (the previous authentication system) and Helsinki-Profile, refer to the [GDPR API documentation](./gdpr/README.md).

## Audit logging

Audit logging is implemented with `django-auditlog`, but it has some extended features applied with [auditlog_extra](https://github.com/City-of-Helsinki/django-auditlog-extra) -app.

The configuration to define which models are in the scope of the audit logging can be found in [auditlog_settings.py](./kukkuu/auditlog_settings.py).

The GraphQL query/mutation and admin site views can be logged by using the mixins and decorators that `auditlog_extra` provides.

**References**:

- Django-auditlog

  > PyPi: https://pypi.org/project/django-auditlog/.
  >
  > Github: https://github.com/jazzband/django-auditlog.
  >
  > Docs: https://django-auditlog.readthedocs.io/en/latest/index.html.

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

To use the SMS notification functionality, you have to acquire an API key from
[Notification Service API](https://github.com/City-of-Helsinki/notification-service-api)
(See [README](https://github.com/City-of-Helsinki/notification-service-api/tree/notification-service-api-v0.5.0?tab=readme-ov-file#api-authentication)).
The following environment variables are needed:

```python
NOTIFICATION_SERVICE_API_TOKEN=your_api_key
NOTIFICATION_SERVICE_API_URL=notification_service_end_point
```

## Releases, changelogs and deployments

The used environments are listed in [Service environments](#service-environments).

The application uses automatic semantic versions and is released using [Release Please](https://github.com/googleapis/release-please).

> Release Please is a GitHub Action that automates releases for you. It will create a GitHub release and a GitHub Pull Request with a changelog based on conventional commits.

Each time you merge a "normal" pull request, the release-please-action will create or update a "Release PR" with the changelog and the version bump related to the changes (they're named like `release-please--branches--master--components--kukkuu-`).

To create a new release for an app, this release PR is merged, which creates a new release with release notes and a new tag. This tag will be picked by Azure pipeline and trigger a new deployment to staging. From there, the release needs to be manually released to production.

When merging release PRs, make sure to use the "Rebase and merge" (or "Squash and merge") option, so that Github doesn't create a merge commit. All the commits must follow the conventional commits format. This is important, because the release-please-action does not work correctly with merge commits (there's an open issue you can track: [Chronological commit sorting means that merged PRs can be ignored ](https://github.com/googleapis/release-please/issues/1533)).

See [Release Please Implementation Design](https://github.com/googleapis/release-please/blob/main/docs/design.md) for more details.

And all docs are available here: [release-please docs](https://github.com/googleapis/release-please/tree/main/docs).

### Conventional Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) to ensure that the changelogs are generated correctly.

### Releasable units

Release please goes through commits and tries to find "releasable units" using commit messages as guidance - it will then add these units to their respective release PR's and figures out the version number from the types: `fix` for patch, `feat` for minor, `feat!` for major. None of the other types will be included in the changelog. So, you can use for example `chore` or `refactor` to do work that does not need to be included in the changelog and won't bump the version.

### Configuration

The release-please workflow is located in the [release-please.yml](./.github/workflows/release-please.yml) file.

The configuration for release-please is located in the [release-please-config.json](./release-please-config.json) file.
See all the options here: [release-please docs](https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md).

The manifest file is located in the [release-please-manifest.json](./.release-please-manifest.json) file.

When adding a new app, add it to both the [release-please-config.json](./release-please-config.json) and [release-please-manifest.json](./.release-please-manifest.json) file with the current version of the app. After this, release-please will keep track of versions with [release-please-manifest.json](./.release-please-manifest.json).

### Troubleshoting release-please

If you were expecting a new release PR to be created or old one to be updated, but nothing happened, there's probably one of the older release PR's in pending state or action didn't run.

1. Check if the release action ran for the last merge to main. If it didn't, run the action manually with a label.
2. Check if there's any open release PR. If there is, the work is now included on this one (this is the normal scenario).
3. If you do not see any open release PR related to the work, check if any of the closed PR's are labeled with `autorelease: pending` - ie. someone might have closed a release PR manually. Change the closed PR's label to `autorelease: tagged`. Then go and re-run the last merge workflow to trigger the release action - a new release PR should now appear.
4. Finally check the output of the release action. Sometimes the bot can't parse the commit message and there is a notification about this in the action log. If this happens, it won't include the work in the commit either. You can fix this by changing the commit message to follow the [Conventional Commits](https://www.conventionalcommits.org/) format and rerun the action.

**Important!** If you have closed a release PR manually, you need to change the label of closed release PR to `autorelease: tagged`. Otherwise, the release action will not create a new release PR.

**Important!** Extra label will force release-please to re-generate PR's. This is done when action is run manually with prlabel -option

Sometimes there might be a merge conflict in release PR - this should resolve itself on the next push to main. It is possible run release-please action manually with label, it should recreate the PR's. You can also resolve it manually, by updating the [release-please-manifest.json](./.release-please-manifest.json) file.

#### Fix merge conflicts by running release-please -action manually

1. Open [release-please github action](https://github.com/City-of-Helsinki/kukkuu/actions/workflows/release-please.yml)
2. Click **Run workflow**
3. Check Branch is **master**
4. Leave label field empty. New label is not needed to fix merge issues
5. Click **Run workflow** -button

There's also a CLI for debugging and manually running releases available for release-please: [release-please-cli](https://github.com/googleapis/release-please/blob/main/docs/cli.md)

### Deployments

When a Release-Please pull request is merged and a version tag is created (or a proper tag name for a commit is manually created), this tag will be picked by Azure pipeline, which then triggers a new deployment to staging. From there, the deployment needs to be manually approved to allow it to proceed to the production environment.

The tag name is defined in the [azure-pipelines-release.yml](./azure-pipelines-release.yml).

## Issues board

https://helsinkisolutionoffice.atlassian.net/projects/KK/issues/?filter=allissues

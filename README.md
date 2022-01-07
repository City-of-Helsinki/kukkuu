# Kukkuu

:baby: Culture Kids (kulttuurin kummilapset) API :violin:

[![status](https://travis-ci.com/City-of-Helsinki/kukkuu.svg)](https://github.com/City-of-Helsinki/kukkuu)
[![codecov](https://codecov.io/gh/City-of-Helsinki/kukkuu/branch/develop/graph/badge.svg)](https://codecov.io/gh/City-of-Helsinki/kukkuu)

## Environments
Production environment:
- https://kukkuu-api.prod.hel.ninja/kukkuu/graphql

Testing environment:
- https://kukkuu.test.kuva.hel.ninja/graphql

## Development with Docker

1. Copy `docker-compose.env.yaml.example` to `docker-compose.env.yaml` and modify it if needed.

2. Run `docker-compose up`

The project is now running at [localhost:8081](http://localhost:8081)

## Development without Docker

Prerequisites:

* PostgreSQL 11
* Python 3.9

### Installing Python requirements

* Run `pip install -r requirements.txt`
* Run `pip install -r requirements-dev.txt` (development requirements)

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

### Notification import

The emails notifications that Kukkuu sends can be imported from a Google Sheets spreadsheet. To do that, first configure setting `KUKKUU_NOTIFICATIONS_SHEET_ID`, and then either

1) run `python manage.py import_notifications` to import and update all the notifications, or
2) use actions in Django admin UI's notification list view to have finer control on which notifications to update and create

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

### Daily running, Debugging

* Create `.env` file: `touch .env`
* Set the `DEBUG` environment variable to `1`.
* Run `python manage.py migrate`
* Run `python manage.py runserver localhost:8081`
* The project is now running at [localhost:8081](http://localhost:8081) 

## GraphQL API Documentation

To view the GraphQL API documentation, in DEBUG mode visit: http://localhost:8081/graphql and checkout the `Documentation Explorer` section

## Report API

For fetching data for reporting purposes there is a separate REST API located at [localhost:8081/reports/](http://localhost:8081/reports/).

The API requires authentication via HTTP basic authentication, or alternatively session authentication when DEBUG is `True`. The accessing user must also have Django permission `reports.access_report_api`.

API documentation of the report API can be viewed at [localhost:8081/reports/schema/redoc/](http://localhost:8081/reports/schema/redoc/).

## Keeping Python requirements up to date

1. Install `pip-tools`:

    * `pip install pip-tools`

2. Add new packages to `requirements.in` or `requirements-dev.in`

3. Update `.txt` file for the changed requirements file:

    * `pip-compile requirements.in`
    * `pip-compile requirements-dev.in`

4. If you want to update dependencies to their newest versions, run:

    * `pip-compile --upgrade requirements.in`

5. To install Python requirements run:

    * `pip-sync requirements.txt`

## Code format

This project uses [`black`](https://github.com/ambv/black) for Python code formatting.
We follow the basic config, without any modifications. Basic `black` commands:

* To let `black` do its magic: `black .`
* To see which files `black` would change: `black --check .`

Or you can use [`pre-commit`](https://pre-commit.com/) to quickly format your code before committing.


1. Install `pre-commit` (there are many ways to do but let's use pip as an example):
    * `pip install pre-commit`
2. Set up git hooks from `.pre-commit-config.yaml`, run this command from project root:
    * `pre-commit install`

After that, formatting hooks will run against all changed files before committing

## Contact infomation

@tuomas777 @quyenlq

## Issues board

https://helsinkisolutionoffice.atlassian.net/projects/KK/issues/?filter=allissues

#!/bin/bash
set -e

# -z for empty / not assigned variable or -o to check whether the value is 0 (=should not be skipped)
if [ -z "$SKIP_DATABASE_CHECK" -o "$SKIP_DATABASE_CHECK" = "0" ]; then
  until nc -z -v -w30 "$DATABASE_HOST" 5432
  do
    echo "Waiting for postgres database connection..."
    sleep 1
  done
  echo "Database is up!"
fi


# Apply database migrations
if [[ "$APPLY_MIGRATIONS" = "1" ]]; then
    echo "Applying database migrations..."
    ./manage.py migrate --noinput
fi

# Add default languages
if [[ "$ADD_DEFAULT_LANGUAGES" = "1" ]]; then
    echo "Adding default languages..."
    ./manage.py add_languages --default
fi

# Start server
if [[ ! -z "$@" ]]; then
    "$@"
elif [[ "$DEV_SERVER" = "1" ]]; then
    python -Wd ./manage.py runserver 0.0.0.0:8081
else
    uwsgi --ini .prod/uwsgi.ini
fi

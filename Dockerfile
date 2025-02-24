# ==============================
FROM registry.access.redhat.com/ubi9/python-311 AS appbase
# ==============================

USER root
WORKDIR /app

RUN mkdir /entrypoint

# chmod=755 = rwxr-xr-x i.e. owner can read, write and execute, group and others can read and execute
COPY --chown=root:root --chmod=755 requirements.txt /app/requirements.txt
COPY --chown=root:root --chmod=755 requirements-not-from-pypi.txt /app/requirements-not-from-pypi.txt
COPY --chown=root:root --chmod=755 requirements-prod.txt /app/requirements-prod.txt

RUN yum update -y && yum install -y \
    nc \
    && pip install -U pip \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir -r /app/requirements-not-from-pypi.txt \
    && pip install --no-cache-dir  -r /app/requirements-prod.txt

#-----------------------------------------------------------
# Please add all files & directories here
# that are needed by both development and production stages:
#-----------------------------------------------------------
#
# Copying directories as part of a multiple COPY command is problematic,
# as dirs are not copied, but only their contents are copied.
# Therefore, we need to copy each dir with a separate COPY command.
#
# Just copying the whole . directory would raise security issue:
# "Copying recursively might inadvertently add sensitive data to the
# container. Recursively copying context directories is security-sensitive",
# see https://rules.sonarsource.com/docker/RSPEC-6470/
WORKDIR /app
COPY --chown=root:root --chmod=755 .release-please-manifest.json .release-please-manifest.json
COPY --chown=root:root --chmod=755 browser-tests browser-tests
COPY --chown=root:root --chmod=755 CHANGELOG.md CHANGELOG.md
COPY --chown=root:root --chmod=755 children children
COPY --chown=root:root --chmod=755 common common
COPY --chown=root:root --chmod=755 custom_health_checks custom_health_checks
COPY --chown=root:root --chmod=755 data data
COPY --chown=root:root --chmod=755 events events
COPY --chown=root:root --chmod=755 gdpr gdpr
COPY --chown=root:root --chmod=755 importers importers
COPY --chown=root:root --chmod=755 kukkuu kukkuu
COPY --chown=root:root --chmod=755 kukkuu_helusers_admin kukkuu_helusers_admin
COPY --chown=root:root --chmod=755 kukkuu_mailer_admin kukkuu_mailer_admin
COPY --chown=root:root --chmod=755 languages languages
COPY --chown=root:root --chmod=755 LICENSE LICENSE
COPY --chown=root:root --chmod=755 manage.py manage.py
COPY --chown=root:root --chmod=755 messaging messaging
COPY --chown=root:root --chmod=755 projects projects
COPY --chown=root:root --chmod=755 pyproject.toml pyproject.toml
COPY --chown=root:root --chmod=755 README.md README.md
COPY --chown=root:root --chmod=755 release-please-config.json release-please-config.json
COPY --chown=root:root --chmod=755 reports reports
COPY --chown=root:root --chmod=755 sonar-project.properties sonar-project.properties
COPY --chown=root:root --chmod=755 subscriptions subscriptions
COPY --chown=root:root --chmod=755 users users
COPY --chown=root:root --chmod=755 utils utils
COPY --chown=root:root --chmod=755 venues venues
COPY --chown=root:root --chmod=755 verification_tokens verification_tokens

COPY --chown=root:root --chmod=755 docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
ENTRYPOINT ["/entrypoint/docker-entrypoint.sh"]

# ==============================
FROM appbase AS development
# ==============================

COPY --chown=root:root --chmod=755 requirements-dev.txt /app/requirements-dev.txt
RUN pip install --no-cache-dir -r /app/requirements-dev.txt

ENV DEV_SERVER=1

# fatal: detected dubious ownership in repository at '/app'
RUN git config --system --add safe.directory /app

USER default
EXPOSE 8081/tcp

# ==============================
FROM appbase AS production
# ==============================

# Please add all files & directories here that are only needed in production:
COPY --chown=root:root --chmod=755 .prod /app/.prod

# fatal: detected dubious ownership in repository at '/app'
RUN git config --system --add safe.directory /app

RUN SECRET_KEY="only-used-for-collectstatic" KUKKUU_HASHID_SALT="only-used-for-collectstatic" python manage.py collectstatic

USER default
EXPOSE 8000/tcp

# branch or tag used to pull python-uwsgi-common.
ARG UWSGI_COMMON_REF=main

# ==============================
FROM registry.access.redhat.com/ubi9/python-312 AS appbase
# ==============================

# Re-define args, otherwise those aren't available after FROM directive.
ARG UWSGI_COMMON_REF

USER root
WORKDIR /app

# Install uv, see https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.11.32@sha256:df4cae8f3a96d175e2e5f992e597550000edbe78fdc2594d5cd8de1a217f504c /uv /uvx /usr/local/bin/

ENV UV_PROJECT_ENVIRONMENT=/opt/app-root \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_PYTHON_DOWNLOADS=never
ENV PATH="/opt/app-root/bin:$PATH"

RUN mkdir /entrypoint

# chmod=755 = rwxr-xr-x i.e. owner can read, write and execute, group and others can read and execute.
#
# Related to SonarCloud security hotspot docker:S6470 i.e.
# "Recursively copying context directories is security-sensitive" i.e.
# https://rules.sonarsource.com/docker/RSPEC-6470/
# see .dockerignore for info on what is not copied here:
COPY --chown=root:root --chmod=755 . /app/

RUN yum update -y && yum install -y \
    nc \
    && uv sync --locked --no-default-groups --group prod \
    && uwsgi --build-plugin https://github.com/City-of-Helsinki/uwsgi-sentry \
    && yum clean all

# fatal: detected dubious ownership in repository at '/app'
RUN git config --system --add safe.directory /app

# Build and copy specific python-uwsgi-common files.
ADD https://github.com/City-of-Helsinki/python-uwsgi-common/archive/${UWSGI_COMMON_REF}.tar.gz /usr/src/
RUN mkdir -p /usr/src/python-uwsgi-common && \
    tar --strip-components=1 -xzf /usr/src/${UWSGI_COMMON_REF}.tar.gz -C /usr/src/python-uwsgi-common && \
    cp /usr/src/python-uwsgi-common/uwsgi-base.ini /app && \
    uwsgi --build-plugin /usr/src/python-uwsgi-common && \
    rm -rf /usr/src/${UWSGI_COMMON_REF}.tar.gz && \
    rm -rf /usr/src/python-uwsgi-common


COPY --chown=root:root --chmod=755 docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
ENTRYPOINT ["/entrypoint/docker-entrypoint.sh"]

# ==============================
FROM appbase AS development
# ==============================

RUN uv sync --locked --group prod

ENV DEV_SERVER=1

USER default
EXPOSE 8081/tcp

# ==============================
FROM appbase AS production
# ==============================

RUN SECRET_KEY="only-used-for-collectstatic" KUKKUU_HASHID_SALT="only-used-for-collectstatic" python manage.py collectstatic

USER default
EXPOSE 8000/tcp

# ==============================
FROM registry.access.redhat.com/ubi9/python-311 AS appbase
# ==============================

USER root
WORKDIR /app

RUN mkdir /entrypoint

COPY --chown=default:root requirements.txt /app/requirements.txt
COPY --chown=default:root requirements-not-from-pypi.txt /app/requirements-not-from-pypi.txt
COPY --chown=default:root requirements-prod.txt /app/requirements-prod.txt

RUN yum update -y && yum install -y \
    nc \
    && pip install -U pip \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir -r /app/requirements-not-from-pypi.txt \
    && pip install --no-cache-dir  -r /app/requirements-prod.txt

COPY --chown=default:root docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
ENTRYPOINT ["/entrypoint/docker-entrypoint.sh"]

# ==============================
FROM appbase AS development
# ==============================

COPY --chown=default:root requirements-dev.txt /app/requirements-dev.txt
RUN pip install --no-cache-dir -r /app/requirements-dev.txt

ENV DEV_SERVER=1

COPY --chown=default:root . /app/

# fatal: detected dubious ownership in repository at '/app'
RUN git config --system --add safe.directory /app

USER default
EXPOSE 8081/tcp

# ==============================
FROM appbase AS production
# ==============================

COPY --chown=default:root . /app/

# fatal: detected dubious ownership in repository at '/app'
RUN git config --system --add safe.directory /app

RUN SECRET_KEY="only-used-for-collectstatic" KUKKUU_HASHID_SALT="only-used-for-collectstatic" python manage.py collectstatic

USER default
EXPOSE 8000/tcp

# ==============================
FROM registry.access.redhat.com/ubi8/python-39 as appbase
# ==============================

USER root
WORKDIR /app

RUN mkdir /entrypoint

COPY --chown=default:1001 requirements.txt /app/requirements.txt
COPY --chown=default:1001 requirements-prod.txt /app/requirements-prod.txt

RUN yum update -y && yum install -y \
    nc \
    && pip install -U pip \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir  -r /app/requirements-prod.txt

COPY --chown=default:1001 docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
ENTRYPOINT ["/entrypoint/docker-entrypoint.sh"]

# ==============================
FROM appbase as development
# ==============================

COPY --chown=default:1001 requirements-dev.txt /app/requirements-dev.txt
RUN pip install --no-cache-dir -r /app/requirements-dev.txt

ENV DEV_SERVER=1

COPY --chown=default:1001 . /app/

USER default
EXPOSE 8081/tcp

# ==============================
FROM appbase as production
# ==============================

COPY --chown=default:1001 . /app/

RUN SECRET_KEY="only-used-for-collectstatic" KUKKUU_HASHID_SALT="only-used-for-collectstatic" python manage.py collectstatic

USER default
EXPOSE 8000/tcp

import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import environ
import sentry_sdk
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from helusers.defaults import SOCIAL_AUTH_PIPELINE  # noqa: F401
from jose import ExpiredSignatureError
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.types import Event, Hint

from kukkuu.consts import CSP
from kukkuu.exceptions import AuthenticationExpiredError
from kukkuu.tests.utils.jwt_utils import is_valid_256_bit_key

checkout_dir = environ.Path(__file__) - 2
assert os.path.exists(checkout_dir("manage.py"))

parent_dir = checkout_dir.path("..")
if os.path.isdir(parent_dir("etc")):
    env_file = parent_dir("etc/env")
    default_var_root = environ.Path(parent_dir("var"))
else:
    env_file = checkout_dir(".env")
    default_var_root = environ.Path(checkout_dir("var"))

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, ""),
    MEDIA_ROOT=(environ.Path(), environ.Path(checkout_dir("var"))("media")),
    STATIC_ROOT=(environ.Path(), default_var_root("static")),
    MEDIA_URL=(str, "/media/"),
    STATIC_URL=(str, "/static/"),
    ALLOWED_HOSTS=(list, []),
    USE_X_FORWARDED_HOST=(bool, False),
    DATABASE_URL=(str, ""),
    CACHE_URL=(str, "locmemcache://"),
    MAILER_EMAIL_BACKEND=(str, "django.core.mail.backends.console.EmailBackend"),
    MAILER_LOCK_PATH=(str, ""),
    DEFAULT_FROM_EMAIL=(str, "kukkuu@example.com"),
    DEFAULT_SMS_SENDER=(str, "Hel.fi"),
    ILMOITIN_TRANSLATED_FROM_EMAIL=(dict, {}),
    TRANSLATED_SMS_SENDER=(dict, {}),
    MAIL_MAILGUN_KEY=(str, ""),
    MAIL_MAILGUN_DOMAIN=(str, ""),
    MAIL_MAILGUN_API=(str, ""),
    NOTIFICATION_SERVICE_API_TOKEN=(str, ""),
    NOTIFICATION_SERVICE_API_URL=(str, "https://notification-service.hel.fi/v1/"),
    SENTRY_DSN=(str, ""),
    SENTRY_ENVIRONMENT=(str, ""),
    CORS_ALLOWED_ORIGINS=(list, []),
    CORS_ALLOWED_ORIGIN_REGEXES=(list, []),
    CORS_ORIGIN_ALLOW_ALL=(bool, False),
    SOCIAL_AUTH_TUNNISTAMO_KEY=(str, ""),
    SOCIAL_AUTH_TUNNISTAMO_SECRET=(str, ""),
    SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT=(str, ""),
    TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX=(str, ""),
    TOKEN_AUTH_REQUIRE_SCOPE_PREFIX=(bool, False),
    TOKEN_AUTH_ACCEPTED_AUDIENCE=(list, ["https://api.hel.fi/auth/kukkuu"]),
    TOKEN_AUTH_AUTHSERVER_URL=(
        list,
        ["https://tunnistus.test.hel.ninja/auth/realms/helsinkitunnistus"],
    ),
    ILMOITIN_QUEUE_NOTIFICATIONS=(bool, True),
    STORAGES_DEFAULT_BACKEND=(str, "django.core.files.storage.FileSystemStorage"),
    AZURE_ACCOUNT_NAME=(str, ""),
    AZURE_ACCOUNT_KEY=(str, ""),
    AZURE_CONTAINER=(str, ""),
    AZURE_URL_EXPIRATION_SECS=(str, None),
    AZURE_BLOB_STORAGE_SAS_TOKEN=(str, ""),
    ENABLE_GRAPHIQL=(bool, False),
    KUKKUU_UI_BASE_URL=(str, "http://localhost:3000"),
    KUKKUU_TICKET_VERIFICATION_URL=(str, ""),
    KUKKUU_HASHID_SALT=(str, None),
    KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY=(int, 60),
    KUKKUU_DEFAULT_EVENT_DURATION=(int, 120),
    KUKKUU_REMINDER_DAYS_IN_ADVANCE=(int, 3),
    KUKKUU_FEEDBACK_NOTIFICATION_DELAY=(int, 15),
    KUKKUU_NOTIFICATIONS_SHEET_ID=(str, ""),
    KUKKUU_ENROLMENT_UNENROL_HOURS_BEFORE=(int, 48),
    LOGIN_REDIRECT_URL=(str, "/admin/"),
    LOGOUT_REDIRECT_URL=(str, "/admin/"),
    VERIFICATION_TOKEN_VALID_MINUTES=(int, 15),
    VERIFICATION_TOKEN_LENGTH=(int, 8),
    SUBSCRIPTIONS_AUTH_TOKEN_VALID_MINUTES=(int, 30 * 24 * 60),  # 30 days
    SUBSCRIPTIONS_AUTH_TOKEN_LENGTH=(int, 16),
    GDPR_API_QUERY_SCOPE=(str, "gdprquery"),
    GDPR_API_DELETE_SCOPE=(str, "gdprdelete"),
    GDPR_API_AUTHORIZATION_FIELD=(str, "authorization.permissions.scopes"),
    HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED=(bool, False),
    HELUSERS_PASSWORD_LOGIN_DISABLED=(bool, False),
    TOKEN_AUTH_BROWSER_TEST_JWT_256BIT_SIGN_SECRET=(str, None),
    TOKEN_AUTH_BROWSER_TEST_JWT_ISSUER=(list, None),
    TOKEN_AUTH_BROWSER_TEST_ENABLED=(bool, False),
    BROWSER_TEST_PROJECT_YEAR=(int, 1234),
    BROWSER_TEST_PROJECT_NAME=(str, "Browser test"),
    BROWSER_TEST_GROUP_NAME=(str, "Browser test"),
    BROWSER_TEST_AD_GROUP_NAME=(str, "kukkuu_browser_test"),
    KUKKUU_DEFAULT_LOGGING_LEVEL=(str, "INFO"),
    APP_RELEASE=(str, ""),
)

VERIFICATION_TOKEN_VALID_MINUTES = env("VERIFICATION_TOKEN_VALID_MINUTES")
VERIFICATION_TOKEN_LENGTH = env("VERIFICATION_TOKEN_LENGTH")
SUBSCRIPTIONS_AUTH_TOKEN_VALID_MINUTES = env("SUBSCRIPTIONS_AUTH_TOKEN_VALID_MINUTES")
SUBSCRIPTIONS_AUTH_TOKEN_LENGTH = env("SUBSCRIPTIONS_AUTH_TOKEN_LENGTH")

if os.path.exists(env_file):
    env.read_env(env_file)

BASE_DIR = str(checkout_dir)

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "The SECRET_KEY setting must not be empty. "
        "See README.md for instructions how to generate a new secret key."
    )

ALLOWED_HOSTS = env("ALLOWED_HOSTS")
USE_X_FORWARDED_HOST = env("USE_X_FORWARDED_HOST")

DATABASES = {"default": env.db()}

CACHES = {"default": env.cache()}

if env("DEFAULT_FROM_EMAIL"):
    DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
if env("MAIL_MAILGUN_KEY"):
    ANYMAIL = {
        "MAILGUN_API_KEY": env("MAIL_MAILGUN_KEY"),
        "MAILGUN_SENDER_DOMAIN": env("MAIL_MAILGUN_DOMAIN"),
        "MAILGUN_API_URL": env("MAIL_MAILGUN_API"),
    }
EMAIL_BACKEND = "mailer.backend.DbBackend"
MAILER_EMAIL_BACKEND = env("MAILER_EMAIL_BACKEND")

_tmp_mailer_dir = None
if env("MAILER_LOCK_PATH"):
    MAILER_LOCK_PATH = env("MAILER_LOCK_PATH")
else:
    # Create a temporary directory for mailer lock file.
    # Stored as a module-level variable to keep the TemporaryDirectory instance
    # alive for the entire process lifetime.
    #
    # From https://docs.python.org/3/library/tempfile.html#tempfile.TemporaryDirectory
    # "This class securely creates a temporary directory" and
    # "On completion of the context or destruction of the temporary directory object,
    # the newly created temporary directory and all its contents are removed from
    # the filesystem."
    _tmp_mailer_dir = tempfile.TemporaryDirectory(prefix="kukkuu-mailer-")
    MAILER_LOCK_PATH = Path(_tmp_mailer_dir.name) / "mailer_lockfile"

ILMOITIN_TRANSLATED_FROM_EMAIL = env("ILMOITIN_TRANSLATED_FROM_EMAIL")
ILMOITIN_QUEUE_NOTIFICATIONS = env("ILMOITIN_QUEUE_NOTIFICATIONS")

if env("DEFAULT_SMS_SENDER"):
    DEFAULT_SMS_SENDER = env("DEFAULT_SMS_SENDER")

TRANSLATED_SMS_SENDER = env("TRANSLATED_SMS_SENDER")
NOTIFICATION_SERVICE_API_TOKEN = env("NOTIFICATION_SERVICE_API_TOKEN")
NOTIFICATION_SERVICE_API_URL = env("NOTIFICATION_SERVICE_API_URL")

try:
    REVISION = (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .strip()
        .decode("utf-8")
    )
except Exception:
    REVISION = "n/a"


def sentry_before_send(event: Event, hint: Hint):
    """
    Filter out uninformative errors from being sent to Sentry.

    Some Graphene errors are generic Exceptions with unhelpful messages.
    This function filters them out to reduce noise in Sentry.

    NOTE: The `ignore_errors` option is actually deprecated,
    nevertheless it's included in the init configuration.
    See https://github.com/getsentry/sentry-python/issues/149

    Args:
        event: The event that is being sent to Sentry.
        hint: A dictionary containing additional information about the event.

    Returns:
        The event if it should be sent to Sentry, or None if it should be ignored.
    """

    ignored_error_classes = (ExpiredSignatureError, AuthenticationExpiredError)
    if "exc_info" in hint:
        exc_type, exc_value, traceback = hint["exc_info"]
        if isinstance(exc_value, ignored_error_classes):
            return None
    return event


sentry_sdk.init(
    dsn=env("SENTRY_DSN"),
    release=REVISION,
    environment=env("SENTRY_ENVIRONMENT"),
    integrations=[DjangoIntegration()],
    before_send=sentry_before_send,
)
sentry_sdk.integrations.logging.ignore_logger("graphql.execution.utils")

MEDIA_ROOT = env("MEDIA_ROOT")
STATIC_ROOT = env("STATIC_ROOT")
MEDIA_URL = env("MEDIA_URL")
STATIC_URL = env("STATIC_URL")

# For staging env, we use Google Cloud Storage
STORAGES_DEFAULT_BACKEND = env("STORAGES_DEFAULT_BACKEND")

# For prod, it's Azure Storage
if STORAGES_DEFAULT_BACKEND == "storages.backends.azure_storage.AzureStorage":
    AZURE_ACCOUNT_NAME = env("AZURE_ACCOUNT_NAME")
    AZURE_CONTAINER = env("AZURE_CONTAINER")
    AZURE_URL_EXPIRATION_SECS = env("AZURE_URL_EXPIRATION_SECS")
    if env("AZURE_BLOB_STORAGE_SAS_TOKEN"):
        AZURE_SAS_TOKEN = env("AZURE_BLOB_STORAGE_SAS_TOKEN")
        AZURE_ENDP = f"BlobEndpoint=https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net"
        AZURE_CONNECTION_STRING = f"{AZURE_ENDP};"
    else:
        AZURE_ACCOUNT_KEY = env("AZURE_ACCOUNT_KEY")

STORAGES = {
    "default": {
        "BACKEND": STORAGES_DEFAULT_BACKEND,
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

ROOT_URLCONF = "kukkuu.urls"
WSGI_APPLICATION = "kukkuu.wsgi.application"

LANGUAGE_CODE = "fi"
LANGUAGES = (("fi", _("Finnish")), ("en", _("English")), ("sv", _("Swedish")))
TIME_ZONE = "Europe/Helsinki"
USE_I18N = True
USE_TZ = True
# Set to True to enable GraphiQL interface, this will overriden to True if DEBUG=True
ENABLE_GRAPHIQL = env("ENABLE_GRAPHIQL")

INSTALLED_APPS = [
    "helusers.apps.HelusersConfig",
    "helusers.apps.HelusersAdminConfig",
    "kukkuu_helusers_admin",  # must be after `helusers`, since it overrides admin
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "csp",
    "graphene_django",
    "parler",
    "anymail",
    "mailer",
    "kukkuu_mailer_admin",  # must be after `mailer`, since it overrides admin
    "django_ilmoitin",
    "django_filters",
    "auditlog",
    "guardian",
    "rest_framework",
    "drf_spectacular",
    "health_check",  # requirement
    "social_django",  # For django-admin Keycloak login
    # local apps
    "custom_health_checks",
    "users",
    "children",
    "utils",
    "projects",
    "events",
    "venues",
    "languages",
    "subscriptions",
    "messaging",
    "importers",
    "reports",
    "verification_tokens",
    "auditlog_extra",
    "kukkuu",
    "django_cleanup.apps.CleanupConfig",  # This must be included last
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "auditlog_extra.middleware.AuditlogMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOWED_ORIGIN_REGEXES = env("CORS_ALLOWED_ORIGIN_REGEXES")
CORS_ORIGIN_ALLOW_ALL = env("CORS_ORIGIN_ALLOW_ALL")

# Configure the default CSP rule for different source types
CSP_DEFAULT_SRC = ["'self'"]

# CSP_STYLE_SRC includes 'unsafe-inline' for inline styles added by `django-helusers`
# and `SpectacularRedocView`.
CSP_STYLE_SRC = [
    CSP.SELF,
    CSP.UNSAFE_INLINE,
    "cdn.jsdelivr.net",
    "fonts.googleapis.com",
]

# CSP_SCRIPT_SRC includes 'unsafe-eval' for inline scripts added by
# `SpectacularRedocView`
CSP_SCRIPT_SRC = [
    CSP.SELF,
    CSP.UNSAFE_EVAL,
    "cdn.jsdelivr.net",
    "blob:",
]

# CSP_FONT_SRC includes Google fonts fetched by `SpectacularRedocView`
CSP_FONT_SRC = [
    CSP.SELF,
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "data:",  # /graphql/ endpoint uses "data:font/woff2"
]

# CSP_IMG_SRC includes sources for images fetched by `SpectacularRedocView`
CSP_IMG_SRC = [
    CSP.SELF,
    "cdn.redoc.ly",
    "blob:",
    "data:",
]

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "helusers.tunnistamo_oidc.TunnistamoOIDCAuth",  # For django-admin Keycloak login
    "django.contrib.auth.backends.ModelBackend",
    "kukkuu.oidc.BrowserTestAwareJWTAuthentication",
    "guardian.backends.ObjectPermissionBackend",
]

# Environment variables required for django-admin Keycloak login:
# (See https://github.com/City-of-Helsinki/django-helusers/blob/v0.13.0/README.md)
LOGIN_REDIRECT_URL = env("LOGIN_REDIRECT_URL")
LOGOUT_REDIRECT_URL = env("LOGOUT_REDIRECT_URL")
SOCIAL_AUTH_TUNNISTAMO_KEY = env("SOCIAL_AUTH_TUNNISTAMO_KEY")
SOCIAL_AUTH_TUNNISTAMO_SECRET = env("SOCIAL_AUTH_TUNNISTAMO_SECRET")
SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT = env("SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT")
if not SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT:
    try:
        SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT = env("TOKEN_AUTH_AUTHSERVER_URL")[0]
    except IndexError:
        raise ImproperlyConfigured(
            "Either SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT or TOKEN_AUTH_AUTHSERVER_URL "
            "is needed to enable django-admin Keycloak login"
        )

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ANONYMOUS_USER_NAME = None  # we don't need django-guardian's AnonymousUser

OIDC_API_TOKEN_AUTH = {
    "AUDIENCE": env("TOKEN_AUTH_ACCEPTED_AUDIENCE"),
    "API_SCOPE_PREFIX": env("TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX"),
    "ISSUER": env("TOKEN_AUTH_AUTHSERVER_URL"),
    "REQUIRE_API_SCOPE_FOR_AUTHENTICATION": env("TOKEN_AUTH_REQUIRE_SCOPE_PREFIX"),
    "API_AUTHORIZATION_FIELD": env("GDPR_API_AUTHORIZATION_FIELD"),
}

OIDC_AUTH = {"OIDC_LEEWAY": 60 * 60}

OIDC_BROWSER_TEST_API_TOKEN_AUTH = {
    "ENABLED": env("TOKEN_AUTH_BROWSER_TEST_ENABLED"),
    "JWT_SIGN_SECRET": env("TOKEN_AUTH_BROWSER_TEST_JWT_256BIT_SIGN_SECRET"),
    "ISSUER": env("TOKEN_AUTH_BROWSER_TEST_JWT_ISSUER"),
    "AUDIENCE": env("TOKEN_AUTH_ACCEPTED_AUDIENCE"),
    "API_SCOPE_PREFIX": env("TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX"),
    "REQUIRE_API_SCOPE_FOR_AUTHENTICATION": env("TOKEN_AUTH_REQUIRE_SCOPE_PREFIX"),
    "API_AUTHORIZATION_FIELD": env("GDPR_API_AUTHORIZATION_FIELD"),
}

# Ensure that the browser test JWT authentication is configured properly.
if OIDC_BROWSER_TEST_API_TOKEN_AUTH["ENABLED"]:
    if not OIDC_BROWSER_TEST_API_TOKEN_AUTH["ISSUER"]:
        raise ImproperlyConfigured(
            "API token authentication is enabled, but no issuer is configured. "
            "Set OIDC_BROWSER_TEST_API_TOKEN_AUTH['ISSUER']."
        )
    if not is_valid_256_bit_key(OIDC_BROWSER_TEST_API_TOKEN_AUTH["JWT_SIGN_SECRET"]):
        raise ImproperlyConfigured(
            "JWT secret key for BrowserTestAwareJWTAuthentication must be 256-bits. "
            "Set OIDC_BROWSER_TEST_API_TOKEN_AUTH['JWT_SIGN_SECRET']."
        )

# The browser tests should be targeted for the users of this group.
# If the group does not exist, it will be automatically created,
# when the OIDC_BROWSER_TEST_API_TOKEN_AUTH["ENABLED"] is True.
BROWSER_TEST_PROJECT_YEAR = env("BROWSER_TEST_PROJECT_YEAR")
BROWSER_TEST_PROJECT_NAME = env("BROWSER_TEST_PROJECT_NAME")
BROWSER_TEST_GROUP_NAME = env("BROWSER_TEST_GROUP_NAME") or env(
    "BROWSER_TEST_PROJECT_NAME"
)
BROWSER_TEST_AD_GROUP_NAME = env("BROWSER_TEST_AD_GROUP_NAME")

SITE_ID = 1

PARLER_LANGUAGES = {SITE_ID: ({"code": "fi"}, {"code": "sv"}, {"code": "en"})}

PARLER_SUPPORTED_LANGUAGE_CODES = [x["code"] for x in PARLER_LANGUAGES[SITE_ID]]

PARLER_ENABLE_CACHING = False

GRAPHENE = {
    "SCHEMA": "kukkuu.schema.schema",
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
    ],
}

GRAPHQL_JWT = {"JWT_AUTH_HEADER_PREFIX": "Bearer"}

KUKKUU_MAX_NUM_OF_CHILDREN_PER_GUARDIAN = 100
KUKKUU_QUERY_MAX_DEPTH = 12
KUKKUU_UI_BASE_URL = env("KUKKUU_UI_BASE_URL")
# IF KUKKUU_TICKET_VERIFICATION_URL is set to None,
# the qr code won't be attached to the enrolment notification email.
# Use {reference_id} as a specified value in the given string
# e.g http://localhost:3000/check-ticket-validity/{reference_id}
KUKKUU_TICKET_VERIFICATION_URL = env("KUKKUU_TICKET_VERIFICATION_URL")
# How much an enrolled occurrence can be in the past and still be considered as
# not being in the past. In minutes.
KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY = env(
    "KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY"
)
# If event duration is missing, this will be used as a default value. In minutes.
KUKKUU_DEFAULT_EVENT_DURATION = env("KUKKUU_DEFAULT_EVENT_DURATION")
KUKKUU_DEFAULT_ENROLMENT_LIMIT = 2
KUKKUU_REMINDER_DAYS_IN_ADVANCE = env("KUKKUU_REMINDER_DAYS_IN_ADVANCE")
KUKKUU_FEEDBACK_NOTIFICATION_DELAY = env("KUKKUU_FEEDBACK_NOTIFICATION_DELAY")
KUKKUU_NOTIFICATIONS_SHEET_ID = env("KUKKUU_NOTIFICATIONS_SHEET_ID")
# How many hours before the occurrence start time
# the user can unenrol from the occurrence.
# If set to 0, unenrolment is allowed till the occurrence start.
KUKKUU_ENROLMENT_UNENROL_HOURS_BEFORE = env("KUKKUU_ENROLMENT_UNENROL_HOURS_BEFORE")

KUKKUU_HASHID_MIN_LENGTH = 5
KUKKUU_HASHID_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
KUKKUU_HASHID_SALT = env("KUKKUU_HASHID_SALT")
if KUKKUU_HASHID_SALT is None:
    raise ImproperlyConfigured(
        "KUKKUU_HASHID_SALT must be configured! "
        "Hashids in Kukkuu utils requires the setting!"
    )


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication"
    ]
    + (["rest_framework.authentication.SessionAuthentication"] if DEBUG else []),
    "DEFAULT_PERMISSION_CLASSES": ["reports.drf_permissions.ReportAPIPermission"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"]
    + (["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {"TITLE": "Kukkuu report API", "VERSION": "1.0.0"}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "timestamped_named": {
            "format": "%(asctime)s %(name)s %(levelname)s: %(message)s"
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "timestamped_named"}
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": env("KUKKUU_DEFAULT_LOGGING_LEVEL", None, "INFO"),
        }
    },
}

# GDPR API DOCS - See https://profile-api.dev.hel.ninja/docs/gdpr-api/.
GDPR_API_MODEL = "users.User"
GDPR_API_QUERY_SCOPE = env("GDPR_API_QUERY_SCOPE")
GDPR_API_DELETE_SCOPE = env("GDPR_API_DELETE_SCOPE")
GDPR_API_MODEL_LOOKUP = "uuid"
GDPR_API_URL_PATTERN = "v1/user/<uuid:uuid>"
GDPR_API_USER_PROVIDER = "gdpr.service.get_user"
GDPR_API_DELETER = "gdpr.service.clear_data"

HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED = env("HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED")
HELUSERS_PASSWORD_LOGIN_DISABLED = env("HELUSERS_PASSWORD_LOGIN_DISABLED")

# django-helusers stores access token expiration time as datetime
# and needs a custom serializer to make it serializable to/from JSON:
SESSION_SERIALIZER = "helusers.sessions.TunnistamoOIDCSerializer"

# release information
APP_RELEASE = env("APP_RELEASE")
# get build time from a file in docker image
APP_BUILD_TIME = datetime.fromtimestamp(os.path.getmtime(__file__))

# Load auditlog settings
from kukkuu.auditlog_settings import *  # noqa: E402, F403

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
local_settings_path = os.path.join(checkout_dir(), "local_settings.py")
if os.path.exists(local_settings_path):
    with open(local_settings_path) as fp:
        code = compile(fp.read(), local_settings_path, "exec")
    exec(code, globals(), locals())

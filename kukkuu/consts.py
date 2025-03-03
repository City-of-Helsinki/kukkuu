# Common errors
GENERAL_ERROR = "GENERAL_ERROR"
PERMISSION_DENIED_ERROR = "PERMISSION_DENIED_ERROR"
OBJECT_DOES_NOT_EXIST_ERROR = "OBJECT_DOES_NOT_EXIST_ERROR"
DATA_VALIDATION_ERROR = "DATA_VALIDATION_ERROR"
API_USAGE_ERROR = "API_USAGE_ERROR"

# Kukkuu specific errors
MAX_NUMBER_OF_CHILDREN_PER_GUARDIAN_ERROR = "MAX_NUMBER_OF_CHILDREN_PER_GUARDIAN_ERROR"
CHILD_ALREADY_JOINED_EVENT_ERROR = "CHILD_ALREADY_JOINED_EVENT_ERROR"
PAST_OCCURRENCE_ERROR = "PAST_OCCURRENCE_ERROR"
OCCURRENCE_IS_FULL_ERROR = "OCCURRENCE_IS_FULL_ERROR"
OCCURRENCE_MISMATCH_ERROR = "OCCURRENCE_MISMATCH_ERROR"
EVENT_ALREADY_PUBLISHED_ERROR = "EVENT_ALREADY_PUBLISHED_ERROR"
EVENT_GROUP_ALREADY_PUBLISHED_ERROR = "EVENT_GROUP_ALREADY_PUBLISHED_ERROR"
EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR = (
    "EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR"
)
EVENT_NOT_PUBLISHED_ERROR = "EVENT_NOT_PUBLISHED_ERROR"
MISSING_DEFAULT_TRANSLATION_ERROR = "MISSING_DEFAULT_TRANSLATION_ERROR"
INELIGIBLE_OCCURRENCE_ENROLMENT = "INELIGIBLE_OCCURRENCE_ENROLMENT"
INVALID_EMAIL_FORMAT_ERROR = "INVALID_EMAIL_FORMAT_ERROR"
ALREADY_SUBSCRIBED_ERROR = "ALREADY_SUBSCRIBED_ERROR"
OCCURRENCE_IS_NOT_FULL_ERROR = "OCCURRENCE_IS_NOT_FULL_ERROR"
MESSAGE_ALREADY_SENT_ERROR = "MESSAGE_ALREADY_SENT_ERROR"
PAST_ENROLMENT_ERROR = "PAST_ENROLMENT_ERROR"
SINGLE_EVENTS_DISALLOWED_ERROR = "SINGLE_EVENTS_DISALLOWED_ERROR"
TICKET_SYSTEM_URL_MISSING_ERROR = "TICKET_SYSTEM_URL_MISSING_ERROR"
NO_FREE_TICKET_SYSTEM_PASSWORDS_ERROR = "NO_FREE_TICKET_SYSTEM_PASSWORDS_ERROR"
TICKET_SYSTEM_PASSWORD_NOTHING_TO_IMPORT_ERROR = (
    "TICKET_SYSTEM_PASSWORD_NOTHING_TO_IMPORT_ERROR"
)
TICKET_SYSTEM_PASSWORD_ALREADY_ASSIGNED_ERROR = (
    "TICKET_SYSTEM_PASSWORD_ALREADY_ASSIGNED_ERROR"
)
UNAUTHENTICATED_ERROR = "UNAUTHENTICATED_ERROR"
AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
AUTHENTICATION_EXPIRED_ERROR = "AUTHENTICATION_EXPIRED_ERROR"
VERIFICATION_TOKEN_INVALID_ERROR = "VERIFICATION_TOKEN_INVALID_ERROR"


class CSP:
    """The “special” source values of 'self', 'unsafe-inline', 'unsafe-eval', 'none'
    and hash-source ('sha256-...') must be quoted! e.g.: CSP_DEFAULT_SRC = ("'self'",).
    Without quotes they will not work as intended.
    Ref. https://django-csp.readthedocs.io/en/stable/configuration.html.
    """

    SELF = "'self'"
    NONE = "'none'"
    UNSAFE_INLINE = "'unsafe-inline'"
    UNSAFE_EVAL = "'unsafe-eval'"


class PostgresSslMode:
    """
    PostgreSQL database connection's SSL mode values.

    Documentation copied from https://www.postgresql.org/docs/13/libpq-connect.html

    For a detailed description of how these modes work, see PostgreSQL documentation
    at https://www.postgresql.org/docs/13/libpq-ssl.html

    "This option determines whether or with what priority a secure SSL TCP/IP
    connection will be negotiated with the server. There are six modes:

    disable
        only try a non-SSL connection

    allow
        first try a non-SSL connection; if that fails, try an SSL connection

    prefer (default)
        first try an SSL connection; if that fails, try a non-SSL connection

    require
        only try an SSL connection. If a root CA file is present, verify the
        certificate in the same way as if verify-ca was specified

    verify-ca
        only try an SSL connection, and verify that the server certificate is
        issued by a trusted certificate authority (CA)

    verify-full
        only try an SSL connection, verify that the server certificate is issued
        by a trusted CA and that the requested server host name matches that in
        the certificate"
    """

    DISABLE = "disable"
    ALLOW = "allow"
    PREFER = "prefer"
    REQUIRE = "require"
    VERIFY_CA = "verify-ca"
    VERIFY_FULL = "verify-full"

    @staticmethod
    def get_default():
        return PostgresSslMode.PREFER

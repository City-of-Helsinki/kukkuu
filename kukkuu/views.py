from typing import Optional

import sentry_sdk
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from graphene.validation import depth_limit_validator
from graphene_file_upload.django import FileUploadGraphQLView
from graphql import ExecutionResult
from graphql_jwt.exceptions import PermissionDenied as GraphQLJWTPermissionDenied
from helusers.oidc import AuthenticationError

from kukkuu.consts import (
    ALREADY_SUBSCRIBED_ERROR,
    API_USAGE_ERROR,
    AUTHENTICATION_ERROR,
    AUTHENTICATION_EXPIRED_ERROR,
    CHILD_ALREADY_JOINED_EVENT_ERROR,
    DATA_VALIDATION_ERROR,
    EVENT_ALREADY_PUBLISHED_ERROR,
    EVENT_GROUP_ALREADY_PUBLISHED_ERROR,
    EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR,
    EVENT_NOT_PUBLISHED_ERROR,
    GENERAL_ERROR,
    INELIGIBLE_OCCURRENCE_ENROLMENT,
    INVALID_EMAIL_FORMAT_ERROR,
    MAX_NUMBER_OF_CHILDREN_PER_GUARDIAN_ERROR,
    MESSAGE_ALREADY_SENT_ERROR,
    MISSING_DEFAULT_TRANSLATION_ERROR,
    NO_FREE_TICKET_SYSTEM_PASSWORDS_ERROR,
    OBJECT_DOES_NOT_EXIST_ERROR,
    OCCURRENCE_IS_FULL_ERROR,
    OCCURRENCE_IS_NOT_FULL_ERROR,
    OCCURRENCE_MISMATCH_ERROR,
    PAST_ENROLMENT_ERROR,
    PAST_OCCURRENCE_ERROR,
    PERMISSION_DENIED_ERROR,
    SINGLE_EVENTS_DISALLOWED_ERROR,
    TICKET_SYSTEM_PASSWORD_ALREADY_ASSIGNED_ERROR,
    TICKET_SYSTEM_PASSWORD_NOTHING_TO_IMPORT_ERROR,
    TICKET_SYSTEM_URL_MISSING_ERROR,
    TOO_LATE_TO_UNENROL_ERROR,
    VERIFICATION_TOKEN_INVALID_ERROR,
)
from kukkuu.exceptions import (
    AlreadySubscribedError,
    ApiUsageError,
    AuthenticationExpiredError,
    ChildAlreadyJoinedEventError,
    DataValidationError,
    EventAlreadyPublishedError,
    EventGroupAlreadyPublishedError,
    EventGroupNotReadyForPublishingError,
    EventNotPublishedError,
    IneligibleOccurrenceEnrolment,
    InvalidEmailFormatError,
    KukkuuGraphQLError,
    MaxNumberOfChildrenPerGuardianError,
    MessageAlreadySentError,
    MissingDefaultTranslationError,
    NoFreeTicketSystemPasswordsError,
    ObjectDoesNotExistError,
    OccurrenceIsFullError,
    OccurrenceIsNotFullError,
    OccurrenceYearMismatchError,
    PastEnrolmentError,
    PastOccurrenceError,
    SingleEventsDisallowedError,
    TicketSystemPasswordAlreadyAssignedError,
    TicketSystemPasswordNothingToImportError,
    TicketSystemUrlMissingError,
    TooLateToUnenrolError,
    VerificationTokenInvalidError,
)

error_codes_shared = {
    type(None): GENERAL_ERROR,
    Exception: GENERAL_ERROR,
    ObjectDoesNotExistError: OBJECT_DOES_NOT_EXIST_ERROR,
    PermissionDenied: PERMISSION_DENIED_ERROR,
    GraphQLJWTPermissionDenied: PERMISSION_DENIED_ERROR,
    ApiUsageError: API_USAGE_ERROR,
    DataValidationError: DATA_VALIDATION_ERROR,
    InvalidEmailFormatError: INVALID_EMAIL_FORMAT_ERROR,
}

error_codes_kukkuu = {
    MaxNumberOfChildrenPerGuardianError: MAX_NUMBER_OF_CHILDREN_PER_GUARDIAN_ERROR,
    ChildAlreadyJoinedEventError: CHILD_ALREADY_JOINED_EVENT_ERROR,
    PastOccurrenceError: PAST_OCCURRENCE_ERROR,
    OccurrenceIsFullError: OCCURRENCE_IS_FULL_ERROR,
    OccurrenceYearMismatchError: OCCURRENCE_MISMATCH_ERROR,
    EventAlreadyPublishedError: EVENT_ALREADY_PUBLISHED_ERROR,
    EventGroupAlreadyPublishedError: EVENT_GROUP_ALREADY_PUBLISHED_ERROR,
    MissingDefaultTranslationError: MISSING_DEFAULT_TRANSLATION_ERROR,
    IneligibleOccurrenceEnrolment: INELIGIBLE_OCCURRENCE_ENROLMENT,
    AlreadySubscribedError: ALREADY_SUBSCRIBED_ERROR,
    OccurrenceIsNotFullError: OCCURRENCE_IS_NOT_FULL_ERROR,
    MessageAlreadySentError: MESSAGE_ALREADY_SENT_ERROR,
    EventGroupNotReadyForPublishingError: EVENT_GROUP_NOT_READY_FOR_PUBLISHING_ERROR,
    EventNotPublishedError: EVENT_NOT_PUBLISHED_ERROR,
    PastEnrolmentError: PAST_ENROLMENT_ERROR,
    TooLateToUnenrolError: TOO_LATE_TO_UNENROL_ERROR,
    SingleEventsDisallowedError: SINGLE_EVENTS_DISALLOWED_ERROR,
    TicketSystemUrlMissingError: TICKET_SYSTEM_URL_MISSING_ERROR,
    NoFreeTicketSystemPasswordsError: NO_FREE_TICKET_SYSTEM_PASSWORDS_ERROR,
    TicketSystemPasswordAlreadyAssignedError: (
        TICKET_SYSTEM_PASSWORD_ALREADY_ASSIGNED_ERROR
    ),
    TicketSystemPasswordNothingToImportError: (
        TICKET_SYSTEM_PASSWORD_NOTHING_TO_IMPORT_ERROR
    ),
    AuthenticationError: AUTHENTICATION_ERROR,
    AuthenticationExpiredError: AUTHENTICATION_EXPIRED_ERROR,
    VerificationTokenInvalidError: VERIFICATION_TOKEN_INVALID_ERROR,
}

sentry_ignored_errors = (
    ObjectDoesNotExist,
    PermissionDenied,
    GraphQLJWTPermissionDenied,
    AuthenticationExpiredError,
)

error_codes = {**error_codes_shared, **error_codes_kukkuu}


class SentryGraphQLView(FileUploadGraphQLView):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            validation_rules=[
                depth_limit_validator(max_depth=settings.KUKKUU_QUERY_MAX_DEPTH)
            ],
        )

    def execute_graphql_request(self, request, data, query, *args, **kwargs):
        """Extract any exceptions and send some of them to Sentry"""
        result: Optional[ExecutionResult] = super().execute_graphql_request(
            request, data, query, *args, **kwargs
        )
        if result and result.errors:
            errors_to_sentry = [
                e
                for e in result.errors
                if not isinstance(
                    getattr(e, "original_error", None),
                    (KukkuuGraphQLError,) + sentry_ignored_errors,
                )
            ]
            if errors_to_sentry:
                self._capture_sentry_exceptions(errors_to_sentry, query)
        return result

    def _capture_sentry_exceptions(self, errors, query):
        scope = sentry_sdk.get_current_scope()
        scope.set_extra("graphql_query", query)
        for error in errors:
            if hasattr(error, "original_error"):
                error = error.original_error
            sentry_sdk.capture_exception(error)

    @staticmethod
    def format_error(error):
        def get_error_code(exception):
            """Get the most specific error code for the exception via superclass"""
            for exc in exception.mro():
                try:
                    return error_codes[exc]
                except KeyError:
                    continue

        try:
            error_code = get_error_code(error.original_error.__class__)
        except AttributeError:
            error_code = GENERAL_ERROR

        formatted_error = super(SentryGraphQLView, SentryGraphQLView).format_error(
            error
        )
        if error_code and (
            isinstance(formatted_error, dict)
            and not (
                "extensions" in formatted_error
                and "code" in formatted_error["extensions"]
            )
        ):
            formatted_error["extensions"] = {"code": error_code}
        return formatted_error

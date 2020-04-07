import sentry_sdk
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from graphene_file_upload.django import FileUploadGraphQLView
from graphql_jwt.exceptions import PermissionDenied as JwtPermissionDenied

from kukkuu.consts import (
    API_USAGE_ERROR,
    CHILD_ALREADY_JOINED_EVENT_ERROR,
    DATA_VALIDATION_ERROR,
    EVENT_ALREADY_PUBLISHED_ERROR,
    GENERAL_ERROR,
    MAX_NUMBER_OF_CHILDREN_PER_GUARDIAN_ERROR,
    MISSING_DEFAULT_TRANSLATION_ERROR,
    OBJECT_DOES_NOT_EXIST_ERROR,
    OCCURRENCE_IS_FULL_ERROR,
    PAST_OCCURRENCE_ERROR,
    PERMISSION_DENIED_ERROR,
)
from kukkuu.exceptions import (
    ApiUsageError,
    ChildAlreadyJoinedEventError,
    DataValidationError,
    EventAlreadyPublishedError,
    KukkuuGraphQLError,
    MaxNumberOfChildrenPerGuardianError,
    MissingDefaultTranslationError,
    ObjectDoesNotExistError,
    OccurrenceIsFullError,
    PastOccurrenceError,
)

error_codes_shared = {
    Exception: GENERAL_ERROR,
    ObjectDoesNotExistError: OBJECT_DOES_NOT_EXIST_ERROR,
    JwtPermissionDenied: PERMISSION_DENIED_ERROR,
    PermissionDenied: PERMISSION_DENIED_ERROR,
    ApiUsageError: API_USAGE_ERROR,
    DataValidationError: DATA_VALIDATION_ERROR,
}

error_codes_kukkuu = {
    MaxNumberOfChildrenPerGuardianError: MAX_NUMBER_OF_CHILDREN_PER_GUARDIAN_ERROR,
    ChildAlreadyJoinedEventError: CHILD_ALREADY_JOINED_EVENT_ERROR,
    PastOccurrenceError: PAST_OCCURRENCE_ERROR,
    OccurrenceIsFullError: OCCURRENCE_IS_FULL_ERROR,
    EventAlreadyPublishedError: EVENT_ALREADY_PUBLISHED_ERROR,
    MissingDefaultTranslationError: MISSING_DEFAULT_TRANSLATION_ERROR,
}

sentry_ignored_errors = (
    ObjectDoesNotExist,
    JwtPermissionDenied,
    PermissionDenied,
)

error_codes = {**error_codes_shared, **error_codes_kukkuu}


class SentryGraphQLView(FileUploadGraphQLView):
    def execute_graphql_request(self, request, data, query, *args, **kwargs):
        """Extract any exceptions and send some of them to Sentry"""
        result = super().execute_graphql_request(request, data, query, *args, **kwargs)
        # If 'invalid' is set, it's a bad request
        if result and result.errors and not result.invalid:
            errors = [
                e
                for e in result.errors
                if not isinstance(
                    getattr(e, "original_error", None), KukkuuGraphQLError
                )
            ]
            if errors:
                self._capture_sentry_exceptions(result.errors, query)
        return result

    def _capture_sentry_exceptions(self, errors, query):
        with sentry_sdk.configure_scope() as scope:
            scope.set_extra("graphql_query", query)
            for error in errors:
                if hasattr(error, "original_error"):
                    error = error.original_error
                sentry_sdk.capture_exception(error)

    @staticmethod
    def format_error(error):
        def get_error_code(exception):
            """Get the most specific error code for the exception via superclass"""
            for exception in exception.mro():
                try:
                    return error_codes[exception]
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

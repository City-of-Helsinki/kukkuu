import sentry_sdk
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from graphene_file_upload.django import FileUploadGraphQLView
from graphql.backend.core import GraphQLCoreBackend
from graphql.language.ast import (
    Field,
    FragmentDefinition,
    FragmentSpread,
    InlineFragment,
    OperationDefinition,
)
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
    QUERY_TOO_DEEP_ERROR,
    SINGLE_EVENTS_DISALLOWED_ERROR,
    TICKET_SYSTEM_URL_MISSING_ERROR,
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
    QueryTooDeepError,
    SingleEventsDisallowedError,
    TicketSystemUrlMissingError,
)

error_codes_shared = {
    Exception: GENERAL_ERROR,
    ObjectDoesNotExistError: OBJECT_DOES_NOT_EXIST_ERROR,
    PermissionDenied: PERMISSION_DENIED_ERROR,
    ApiUsageError: API_USAGE_ERROR,
    DataValidationError: DATA_VALIDATION_ERROR,
    QueryTooDeepError: QUERY_TOO_DEEP_ERROR,
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
    PastEnrolmentError: PAST_ENROLMENT_ERROR,
    SingleEventsDisallowedError: SINGLE_EVENTS_DISALLOWED_ERROR,
    TicketSystemUrlMissingError: TICKET_SYSTEM_URL_MISSING_ERROR,
    NoFreeTicketSystemPasswordsError: NO_FREE_TICKET_SYSTEM_PASSWORDS_ERROR,
    AuthenticationError: AUTHENTICATION_ERROR,
    AuthenticationExpiredError: AUTHENTICATION_EXPIRED_ERROR,
}

sentry_ignored_errors = (
    ObjectDoesNotExist,
    PermissionDenied,
    AuthenticationExpiredError,
)

error_codes = {**error_codes_shared, **error_codes_kukkuu}


def get_fragments(definitions):
    return {
        definition.name.value: definition
        for definition in definitions
        if isinstance(definition, FragmentDefinition)
    }


def get_queries_and_mutations(definitions):
    return [
        definition
        for definition in definitions
        if isinstance(definition, OperationDefinition)
    ]


def measure_depth(node, fragments):
    if isinstance(node, FragmentSpread):
        fragment = fragments.get(node.name.value)
        return measure_depth(node=fragment, fragments=fragments)

    elif isinstance(node, Field):
        if node.name.value.lower() in ["__schema", "__introspection"]:
            return 0

        if not node.selection_set:
            return 1

        depths = []
        for selection in node.selection_set.selections:
            depth = measure_depth(node=selection, fragments=fragments)
            depths.append(depth)
        return 1 + max(depths)

    elif (
        isinstance(node, FragmentDefinition)
        or isinstance(node, OperationDefinition)
        or isinstance(node, InlineFragment)
    ):
        depths = []
        for selection in node.selection_set.selections:
            depth = measure_depth(node=selection, fragments=fragments)
            depths.append(depth)
        return max(depths)
    else:
        raise Exception("Unknown node")


def check_max_depth(max_depth, document):
    fragments = get_fragments(document.definitions)
    queries = get_queries_and_mutations(document.definitions)

    for query in queries:
        depth = measure_depth(query, fragments)
        if depth > max_depth:
            raise QueryTooDeepError(
                "Query is too deep - its depth is {} but the max depth is {}".format(
                    depth, max_depth
                )
            )


# Customize GraphQL Backend inspired by
# https://github.com/manesioz/secure-graphene/pull/1/files
class DepthAnalysisBackend(GraphQLCoreBackend):
    def __init__(self, max_depth, executor=None):
        super().__init__(executor=executor)
        self.max_depth = max_depth

    def document_from_string(self, schema, document_string):
        document = super().document_from_string(schema, document_string)

        check_max_depth(max_depth=self.max_depth, document=document.document_ast)

        return document


class SentryGraphQLView(FileUploadGraphQLView):
    def execute_graphql_request(self, request, data, query, *args, **kwargs):
        """Extract any exceptions and send some of them to Sentry"""
        result = super().execute_graphql_request(request, data, query, *args, **kwargs)
        # If 'invalid' is set, it's a bad request
        if result and result.errors and not result.invalid:
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

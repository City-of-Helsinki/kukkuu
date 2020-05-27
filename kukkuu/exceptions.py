from graphql import GraphQLError


class KukkuuGraphQLError(GraphQLError):
    """GraphQLError that is not sent to Sentry."""


class DataValidationError(KukkuuGraphQLError):
    """Error in object validation"""


class ApiUsageError(KukkuuGraphQLError):
    """Wrong API usage"""


class MaxNumberOfChildrenPerGuardianError(KukkuuGraphQLError):
    """
    Number of children belongs to a guardian reached
    settings.KUKKUU_MAX_NUM_OF_CHILDREN_PER_GUARDIAN
    """


class ChildAlreadyJoinedEventError(KukkuuGraphQLError):
    """Child already joined an event"""


class PastOccurrenceError(KukkuuGraphQLError):
    """Error when child join an occurrence in the past"""


class OccurrenceIsFullError(KukkuuGraphQLError):
    """Error when child join an occurrence which is already full"""


class EventAlreadyPublishedError(KukkuuGraphQLError):
    """Error when admin publish event which is already published"""


class ObjectDoesNotExistError(KukkuuGraphQLError):
    """Object does not exist"""


class MissingDefaultTranslationError(KukkuuGraphQLError):
    """Missing default translation for translatable object"""


class IneligibleOccurrenceEnrolment(KukkuuGraphQLError):
    """Ineligible to enrol event"""


class QueryTooDeepError(KukkuuGraphQLError):
    """Query depth exceeded settings.KUKKUU_QUERY_MAX_DEPTH"""


class InvalidEmailFormatError(KukkuuGraphQLError):
    """Invalid email format"""

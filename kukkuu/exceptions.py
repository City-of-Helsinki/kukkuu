from graphql import GraphQLError


class TicketVerificationError(Exception):
    """General error related to ticket verfication"""


class IllegalEnrolmentReferenceId(TicketVerificationError):
    """Illegal Enrolment reference id"""


class EnrolmentReferenceIdDoesNotExist(TicketVerificationError):
    """
    The decoded enrolment reference id
    could not be linked to any of the enrolments
    """


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


class OccurrenceYearMismatchError(KukkuuGraphQLError):
    """Error when an event occurrence has different year from other occurrences"""


class EventAlreadyPublishedError(KukkuuGraphQLError):
    """Error when admin publish event which is already published"""


class EventGroupAlreadyPublishedError(KukkuuGraphQLError):
    """Error when admin publish event group which is already published"""


class EventGroupNotReadyForPublishingError(KukkuuGraphQLError):
    """Event group not ready for publishing"""


class EventNotPublishedError(KukkuuGraphQLError):
    """Event is not published"""


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


class AlreadySubscribedError(KukkuuGraphQLError):
    """Already subscribed"""


class OccurrenceIsNotFullError(KukkuuGraphQLError):
    """Cannot subscribe to free spot notifications because the occurrence is not full"""


class MessageAlreadySentError(KukkuuGraphQLError):
    """Message already sent"""


class PastEnrolmentError(KukkuuGraphQLError):
    """Cannot unenrol because the enrolment is in the past"""


class SingleEventsDisallowedError(KukkuuGraphQLError):
    """Cannot create an event outside event groups"""


class TicketSystemUrlMissingError(KukkuuGraphQLError):
    """Some occurrence of a published external ticket system event is missing ticket
    system URL"""


class NoFreeTicketSystemPasswordsError(KukkuuGraphQLError):
    """A free ticket system password is needed but there isn't any."""


class AuthenticationExpiredError(KukkuuGraphQLError):
    """Authentication expired."""

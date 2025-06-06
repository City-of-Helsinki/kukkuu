from graphql import GraphQLError


class TicketVerificationError(Exception):
    """General error related to ticket verfication"""


class IllegalEnrolmentReferenceId(TicketVerificationError):  # noqa: N818
    """Illegal Enrolment reference id"""


class EnrolmentReferenceIdDoesNotExist(TicketVerificationError):  # noqa: N818
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


class IneligibleOccurrenceEnrolment(KukkuuGraphQLError):  # noqa: N818
    """Ineligible to enrol event"""


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


class TooLateToUnenrolError(KukkuuGraphQLError):
    """Cannot unenrol because the occurrence starts too soon"""


class SingleEventsDisallowedError(KukkuuGraphQLError):
    """Cannot create an event outside event groups"""


class TicketSystemUrlMissingError(KukkuuGraphQLError):
    """Some occurrence of a published external ticket system event is missing ticket
    system URL"""


class NoFreeTicketSystemPasswordsError(KukkuuGraphQLError):
    """A free ticket system password is needed but there isn't any."""


class TicketSystemPasswordAlreadyAssignedError(KukkuuGraphQLError):
    """
    The ticket system password in question has already been assigned to a child/event
    pair or a ticket system password has already been assigned to the child/event pair
    in question.
    """


class TicketSystemPasswordNothingToImportError(KukkuuGraphQLError):
    """Empty list of passwords given"""


class AuthenticationExpiredError(KukkuuGraphQLError):
    """Authentication expired."""


class VerificationTokenInvalidError(KukkuuGraphQLError):
    """Verification token is not active, is expired or is not available for the user"""

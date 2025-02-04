from events.enums import EnrolmentDeniedReason
from kukkuu.exceptions import (
    ChildAlreadyJoinedEventError,
    DataValidationError,
    EventNotPublishedError,
    IneligibleOccurrenceEnrolment,
    KukkuuGraphQLError,
    OccurrenceIsFullError,
    PastOccurrenceError,
    TicketSystemPasswordAlreadyAssignedError,
)


class NotificationType:
    EVENT_PUBLISHED = "event_published"
    EVENT_GROUP_PUBLISHED = "event_group_published"
    OCCURRENCE_ENROLMENT = "occurrence_enrolment"
    OCCURRENCE_UNENROLMENT = "occurrence_unenrolment"
    OCCURRENCE_CANCELLED = "occurrence_cancelled"
    OCCURRENCE_REMINDER = "occurrence_reminder"
    OCCURRENCE_FEEDBACK = "occurrence_feedback"


notification_types_that_need_communication_acceptance = (
    NotificationType.EVENT_PUBLISHED,
    NotificationType.EVENT_GROUP_PUBLISHED,
)


ENROLMENT_DENIED_REASON_TO_GRAPHQL_ERROR: dict[
    EnrolmentDeniedReason, KukkuuGraphQLError
] = {
    EnrolmentDeniedReason.ALREADY_HAS_PASSWORD_TO_EVENT: (
        TicketSystemPasswordAlreadyAssignedError(
            "Child already has a ticket system password to the event"
        )
    ),
    EnrolmentDeniedReason.ALREADY_HAS_PASSWORD_TO_EVENT_GROUP: (
        TicketSystemPasswordAlreadyAssignedError(
            "Child already has a ticket system password to an event in the event group"
        )
    ),
    EnrolmentDeniedReason.ALREADY_JOINED_EVENT: ChildAlreadyJoinedEventError(
        "Child already joined this event"
    ),
    EnrolmentDeniedReason.ALREADY_JOINED_EVENT_GROUP: ChildAlreadyJoinedEventError(
        "Child already joined an event of this event group"
    ),
    EnrolmentDeniedReason.CHILD_NOT_IN_EVENT_GROUP_PROJECT: (
        IneligibleOccurrenceEnrolment(
            "Child does not belong to the project event group"
        )
    ),
    EnrolmentDeniedReason.CHILD_NOT_IN_EVENT_PROJECT: IneligibleOccurrenceEnrolment(
        "Child does not belong to the project event"
    ),
    EnrolmentDeniedReason.EMPTY_EVENT: DataValidationError("Event is empty"),
    EnrolmentDeniedReason.EMPTY_EVENT_GROUP: DataValidationError(
        "Event group is empty"
    ),
    EnrolmentDeniedReason.EVENT_GROUP_NOT_PUBLISHED: EventNotPublishedError(
        "Event group is not published"
    ),
    EnrolmentDeniedReason.EVENT_NOT_PUBLISHED: EventNotPublishedError(
        "Event is not published"
    ),
    EnrolmentDeniedReason.OCCURRENCE_FULL: OccurrenceIsFullError(
        "Maximum enrolments created"
    ),
    EnrolmentDeniedReason.PAST_OCCURRENCE: PastOccurrenceError(
        "Cannot join occurrence in the past"
    ),
    EnrolmentDeniedReason.YEARLY_ENROLMENT_LIMIT_REACHED: IneligibleOccurrenceEnrolment(
        "Yearly enrolment limit has been reached"
    ),
}

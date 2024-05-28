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

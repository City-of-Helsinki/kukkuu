from enum import Enum


class EnrolmentDeniedReason(Enum):
    ALREADY_HAS_PASSWORD_TO_EVENT = "already_has_password_to_event"
    ALREADY_HAS_PASSWORD_TO_EVENT_GROUP = "already_has_password_to_event_group"
    ALREADY_JOINED_EVENT = "already_joined_event"
    ALREADY_JOINED_EVENT_GROUP = "already_joined_event_group"
    CHILD_NOT_IN_EVENT_GROUP_PROJECT = "child_not_in_event_group_project"
    CHILD_NOT_IN_EVENT_PROJECT = "child_not_in_event_project"
    EMPTY_EVENT = "empty_event"
    EMPTY_EVENT_GROUP = "empty_event_group"
    EVENT_GROUP_NOT_PUBLISHED = "event_group_not_published"
    EVENT_NOT_PUBLISHED = "event_not_published"
    OCCURRENCE_FULL = "occurrence_full"
    PAST_OCCURRENCE = "past_occurrence"
    YEARLY_ENROLMENT_LIMIT_REACHED = "yearly_enrolment_limit_reached"

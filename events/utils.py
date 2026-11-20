from datetime import datetime

from django.conf import settings
from django.utils import timezone

from common.utils import get_global_id


def convert_to_localtime_tz(value):
    dt = datetime.combine(datetime.now().date(), value)
    if timezone.is_naive(value):
        # Auto add local timezone to naive time
        return timezone.make_aware(dt).time()
    else:
        return timezone.localtime(dt).time()


def get_event_ui_url(event, child, language):
    return "{}/{}/profile/child/{}/event/{}".format(
        settings.KUKKUU_UI_BASE_URL,
        language,
        get_global_id(child),
        get_global_id(event),
    )


def get_event_group_ui_url(event_group, child, language):
    return "{}/{}/profile/child/{}/event-group/{}".format(
        settings.KUKKUU_UI_BASE_URL,
        language,
        get_global_id(child),
        get_global_id(event_group),
    )


def get_occurrence_ui_url(occurrence, child, language):
    return "{}/{}/profile/child/{}/occurrence/{}".format(
        settings.KUKKUU_UI_BASE_URL,
        language,
        get_global_id(child),
        get_global_id(occurrence),
    )


def get_occurrence_enrol_ui_url(occurrence, child, language):
    return "{}/{}/profile/child/{}/event/{}/occurrence/{}/enrol".format(
        settings.KUKKUU_UI_BASE_URL,
        language,
        get_global_id(child),
        get_global_id(occurrence.event),
        get_global_id(occurrence),
    )

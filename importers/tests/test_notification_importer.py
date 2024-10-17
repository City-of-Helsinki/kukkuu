import pytest
import responses
from django.conf import settings

from common.tests.utils import create_notification_template_in_language
from django_ilmoitin.models import NotificationTemplate
from events.notifications import NotificationType

from ..notification_importer import NotificationImporter
from .utils import serialize_notifications

LANGUAGES = ("fi", "sv", "en")

MOCK_CSV = """,SUBJECT | FI,SUBJECT | SV,SUBJECT | EN,BODY_TEXT | FI,BODY_TEXT | SV,BODY_TEXT | EN\r\n
event_published,event_published fi updated subject,event_published sv updated subject,event_published en updated subject,event_published fi updated body_text,event_published sv updated body_text,event_published en updated body_text\r\n
occurrence_enrolment,occurrence_enrolment fi updated subject,occurrence_enrolment sv updated subject,occurrence_enrolment en updated subject,occurrence_enrolment fi updated body_text,occurrence_enrolment sv updated body_text,occurrence_enrolment en updated body_text"""  # noqa


@pytest.fixture(autouse=True)
def setup(settings, mocked_responses):
    settings.KUKKUU_NOTIFICATIONS_SHEET_ID = "mock-sheet-id"
    settings.PARLER_SUPPORTED_LANGUAGE_CODES = LANGUAGES
    mocked_responses.add(
        responses.GET,
        "https://docs.google.com/spreadsheets/d/mock-sheet-id/export?format=csv",
        body=MOCK_CSV,
        status=200,
        content_type="application/json",
    )


@pytest.fixture
def event_published_notification():
    for language in LANGUAGES:
        create_notification_template_in_language(
            NotificationType.EVENT_PUBLISHED,
            language,
            subject=f"{NotificationType.EVENT_PUBLISHED} "
            f"{language} original subject",
            body_text=f"{NotificationType.EVENT_PUBLISHED} "
            f"{language} original body_text",
        )
    return NotificationTemplate.objects.get(type=NotificationType.EVENT_PUBLISHED)


@pytest.fixture
def occurrence_enrolment_notification():
    for language in ("fi", "en"):
        create_notification_template_in_language(
            NotificationType.OCCURRENCE_ENROLMENT,
            language,
            subject=f"{NotificationType.OCCURRENCE_ENROLMENT} "
            f"{language} original subject",
            body_text=f"{NotificationType.OCCURRENCE_ENROLMENT} "
            f"{language} original body_text",
        )
    return NotificationTemplate.objects.get(type=NotificationType.OCCURRENCE_ENROLMENT)


@pytest.mark.django_db
def test_create_non_existing_and_update_existing_notifications(
    event_published_notification, occurrence_enrolment_notification, snapshot
):
    NotificationImporter().create_missing_and_update_existing_notifications()

    snapshot.assert_match(serialize_notifications(NotificationTemplate.objects.all()))


@pytest.mark.django_db
def test_create_non_existing_notifications(event_published_notification, snapshot):
    NotificationImporter().create_missing_notifications()

    snapshot.assert_match(serialize_notifications(NotificationTemplate.objects.all()))


@pytest.mark.django_db
def test_update_notifications(event_published_notification, snapshot):
    NotificationImporter().update_notifications([event_published_notification])

    snapshot.assert_match(serialize_notifications(NotificationTemplate.objects.all()))


@pytest.mark.django_db
def test_is_notification_in_sync(event_published_notification):
    importer = NotificationImporter()

    assert not importer.is_notification_in_sync(event_published_notification)

    # set the notification to match the csv
    for language in settings.PARLER_SUPPORTED_LANGUAGE_CODES:
        translation_obj, _ = event_published_notification.translations.get_or_create(
            language_code=language
        )
        for field in ("subject", "body_text", "body_html"):
            setattr(
                translation_obj,
                field,
                getattr(translation_obj, field).replace("original", "updated"),
            )
        translation_obj.save()

    assert importer.is_notification_in_sync(event_published_notification)

import base64

import freezegun
import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from guardian.shortcuts import assign_perm, remove_perm
from rest_framework.test import APIClient

from children.factories import (
    ChildFactory,
    ChildWithGuardianFactory,
    ChildWithTwoGuardiansFactory,
)
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
)
from events.models import Enrolment, Occurrence
from languages.models import Language
from languages.services import LanguageService
from reports.drf_permissions import ACCESS_REPORT_API_PERM
from reports.serializers import get_primary_contact_language
from venues.factories import SystemVenueFactory, VenueFactory

CHILDREN_ENDPOINT = "/reports/children/"
EVENTS_ENDPOINT = "/reports/event/"
EVENT_GROUPS_ENDPOINT = "/reports/event-group/"
VENUES_ENDPOINT = "/reports/venue/"


@pytest.fixture(autouse=True)
def languages():
    Language.objects.all().delete()
    for code in ("fin", "swe", "eng"):
        LanguageService.create_from_language_code(code)
    LanguageService.create_option_other()


@pytest.fixture
def user():
    user = get_user_model().objects.create_user(
        username="test_user",
        password="test_password",
    )
    assign_perm(ACCESS_REPORT_API_PERM, user)
    return user


@pytest.fixture
def user_api_client(user):
    api_client = APIClient()
    api_client.user = user
    credentials = b"test_user:test_password"
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Basic {base64.b64encode(credentials).decode('ascii')}"
    )
    return api_client


@pytest.mark.django_db
def test_children_endpoint_not_authenticated(user):
    response = APIClient().get(CHILDREN_ENDPOINT)
    assert response.status_code == 401


@pytest.mark.django_db
def test_children_endpoint_no_permission(user_api_client):
    remove_perm(ACCESS_REPORT_API_PERM, user_api_client.user)
    response = user_api_client.get(CHILDREN_ENDPOINT)
    assert response.status_code == 403


@pytest.mark.django_db
@override_settings(
    # Must be the same as in CI pipeline for the snapshot to be an exact match:
    KUKKUU_HASHID_SALT="almosttopsecret123"
)
def test_children_endpoint(user_api_client, snapshot, django_assert_max_num_queries):
    with freezegun.freeze_time("2021-02-02T12:00:00Z"):
        ChildWithGuardianFactory(
            name="Doe John",
            birthyear=2021,
            postal_code="11111",
            relationship__guardian__language="fi",
            relationship__guardian__languages_spoken_at_home=["fin", "und"],
            relationship__guardian__email="advocate@example.org",
        )

    with freezegun.freeze_time("2021-03-03T01:00:00Z"):
        ChildWithGuardianFactory(
            name="Garcia Isabella",
            birthyear=2021,
            postal_code="22222",
            relationship__guardian__language="sv",
            relationship__guardian__languages_spoken_at_home=["und"],
            relationship__guardian__email="parent@example.org",
        )

    # This guy's registration date should be 2021-04-05 in Helsinki time
    with freezegun.freeze_time("2021-04-04T23:00:00Z"):
        ChildWithGuardianFactory(
            name="Doe Jane",
            birthyear=2020,
            postal_code="33333",
            relationship__guardian__language="en",
            relationship__guardian__email="something@to-fool-factoryboy.net",
        )

    with freezegun.freeze_time("2021-04-05T21:05:00Z"):
        ChildWithTwoGuardiansFactory(
            name="Last name First name",
            birthyear=2020,
            postal_code="44444",
            relationship__guardian__language="en",
            relationship__guardian__email="guardian@example.org",
            relationship2__guardian__language="sv",
            relationship2__guardian__email="advocate@example.org",
        )

    ChildFactory()  # This is an orphan child so she should not be in the results

    with django_assert_max_num_queries(7):
        response = user_api_client.get(CHILDREN_ENDPOINT)
    assert response.status_code == 200, response.content

    json_data = response.json()

    # The result set should be ordered by 'name'
    assert [child["postal_code"] for child in json_data] == [
        "33333",
        "11111",
        "22222",
        "44444",
    ]

    snapshot.assert_match(json_data)


@pytest.mark.parametrize(
    "contact_languages,language",
    [
        [["en", "sv", "fi"], "fi"],
        [["fi", "en", "sv"], "fi"],
        [["en", "sv"], "en"],
        [["en"], "en"],
        [["fi", "en"], "fi"],
        [["sv"], "sv"],
    ],
)
@pytest.mark.django_db
def test_get_primary_contact_language(contact_languages, language):
    assert get_primary_contact_language(contact_languages) == language


@pytest.mark.django_db
def test_filter_by_is_obsolete(user_api_client):
    ChildWithGuardianFactory(relationship__guardian__user__is_active=True)
    ChildWithGuardianFactory(relationship__guardian__user__is_active=False)

    # Test filtering by is_obsolete=True, to fetch all child that are obsolete
    response = user_api_client.get(CHILDREN_ENDPOINT + "?is_obsolete=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["is_obsolete"] is True

    # Test filtering by is_obsolete=False
    response = user_api_client.get(CHILDREN_ENDPOINT + "?is_obsolete=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["is_obsolete"] is False

    response = user_api_client.get(CHILDREN_ENDPOINT)
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.django_db(reset_sequences=True)
@freezegun.freeze_time("2021-04-04T23:00:00Z")
def test_events_endpoint(
    project, user_api_client, snapshot, django_assert_max_num_queries
):
    # Event in a group
    event_group = EventGroupFactory(project=project)
    event_in_group = EventFactory(
        project=project, event_group=event_group, capacity_per_occurrence=20
    )
    OccurrenceFactory.create_batch(2, event=event_in_group, time=timezone.now())

    # Event without group
    event_without_group = EventFactory(
        project=project, event_group=None, capacity_per_occurrence=30
    )
    OccurrenceFactory.create_batch(
        2, event=event_without_group, capacity_override=40, time=timezone.now()
    )

    assert Occurrence.objects.count() == 2 + 2

    # Enrolments
    for occurrence in [
        event_in_group.occurrences.first(),
        event_without_group.occurrences.first(),
    ]:
        EnrolmentFactory.create_batch(2, occurrence=occurrence)

    assert Enrolment.objects.count() == 2 + 2

    with django_assert_max_num_queries(7):
        response = user_api_client.get(EVENTS_ENDPOINT)
    assert response.status_code == 200, response.content

    json_data = response.json()

    assert len(json_data) == 2
    assert len(json_data[0]["occurrences"]) == 2
    assert (
        json_data[0]["enrolment_count"]
        == json_data[0]["occurrences"][0]["enrolment_count"]
        == 2
    )
    assert (
        json_data[0]["reserved_seats"]
        == json_data[0]["occurrences"][0]["reserved_seats"]
        == 4
    )
    assert (
        json_data[1]["enrolment_count"]
        == json_data[1]["occurrences"][0]["enrolment_count"]
        == 2
    )
    assert (
        json_data[1]["reserved_seats"]
        == json_data[1]["occurrences"][0]["reserved_seats"]
        == 4
    )
    snapshot.assert_match(json_data)


@pytest.mark.django_db
def test_events_endpoint_not_authenticated(user):
    response = APIClient().get(EVENTS_ENDPOINT)
    assert response.status_code == 401


@pytest.mark.django_db
def test_events_endpoint_no_permission(user_api_client):
    remove_perm(ACCESS_REPORT_API_PERM, user_api_client.user)
    response = user_api_client.get(EVENTS_ENDPOINT)
    assert response.status_code == 403


@pytest.mark.django_db(reset_sequences=True)
@freezegun.freeze_time("2021-04-04T23:00:00Z")
def test_event_groups_endpoint(
    project, settings, user_api_client, snapshot, django_assert_max_num_queries
):
    event_group = EventGroupFactory(project=project, name="Example Event Group 1")
    event_in_group = EventFactory(
        project=project,
        event_group=event_group,
        capacity_per_occurrence=20,
        name="Example Event",
    )
    occurrence = OccurrenceFactory.create(event=event_in_group, time=timezone.now())
    EnrolmentFactory.create(occurrence=occurrence)

    for n in range(2, 6):
        g = EventGroupFactory(project=project)
        for lang_code, _ in settings.LANGUAGES:
            g.set_current_language(lang_code)
            g.name = f"Example Event Group {n} ({lang_code})"
        g.save()

    with django_assert_max_num_queries(7):
        response = user_api_client.get(EVENT_GROUPS_ENDPOINT)
    assert response.status_code == 200, response.content

    json_data = response.json()

    assert len(json_data) == 5
    assert json_data[0]["enrolment_count"] == 1
    assert json_data[0]["reserved_seats"] == 2
    for i in range(1, 5):
        assert json_data[i]["enrolment_count"] == 0
        assert json_data[i]["reserved_seats"] == 0

    snapshot.assert_match(json_data)


@pytest.mark.django_db(reset_sequences=True)
@freezegun.freeze_time("2021-04-04T23:00:00Z")
def test_event_groups_retrieve_endpoint(
    project, settings, user_api_client, snapshot, django_assert_max_num_queries
):
    event_group = EventGroupFactory(project=project, name="Example Event Group 1")
    for lang_code, _ in settings.LANGUAGES:
        event_group.set_current_language(lang_code)
        event_group.name = f"Example Event Group ({lang_code})"
    event_group.save()
    event_in_group = EventFactory(
        project=project,
        event_group=event_group,
        capacity_per_occurrence=20,
        name="Example Event",
    )
    occurrence = OccurrenceFactory.create(event=event_in_group, time=timezone.now())
    EnrolmentFactory.create(occurrence=occurrence)
    EnrolmentFactory.create(occurrence=occurrence, attended=True)

    with django_assert_max_num_queries(7):
        response = user_api_client.get(f"{EVENT_GROUPS_ENDPOINT}{event_group.id}/")
    assert response.status_code == 200, response.content

    json_data = response.json()

    assert json_data["enrolment_count"] == 2
    assert json_data["enrolled_children_count"] == 2
    assert json_data["enrolled_adults_count"] == 2
    assert json_data["reserved_seats"] == 4
    assert json_data["attended_enrolment_count"] == 1
    assert json_data["attended_count"] == 2
    assert json_data["attended_children_count"] == 1
    assert json_data["attended_adults_count"] == 1
    assert json_data["attended_seats"] == 2
    assert json_data["capacity"] == 20
    assert json_data["project"]["id"] == project.id
    assert json_data["project"]["year"] == project.year

    snapshot.assert_match(json_data)


@pytest.mark.django_db
def test_event_groups_endpoint_not_authenticated(user):
    response = APIClient().get(EVENT_GROUPS_ENDPOINT)
    assert response.status_code == 401
    event_group = EventGroupFactory()
    response = APIClient().get(f"{EVENT_GROUPS_ENDPOINT}{event_group.id}/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_event_groups_endpoint_no_permission(user_api_client):
    remove_perm(ACCESS_REPORT_API_PERM, user_api_client.user)
    response = user_api_client.get(EVENT_GROUPS_ENDPOINT)
    assert response.status_code == 403
    event_group = EventGroupFactory()
    response = user_api_client.get(f"{EVENT_GROUPS_ENDPOINT}{event_group.id}/")
    assert response.status_code == 403


@pytest.mark.django_db(reset_sequences=True)
def test_venues_endpoint(
    project, settings, user_api_client, snapshot, django_assert_max_num_queries
):
    for n in range(1, 6):
        venue = VenueFactory(project=project)
        for lang_code, _ in settings.LANGUAGES:
            venue.set_current_language(lang_code)
            venue.name = f"Example Venue {n} ({lang_code})"
            venue.address = f"Example Address {n} ({lang_code})"
        venue.save()

    with django_assert_max_num_queries(7):
        response = user_api_client.get(VENUES_ENDPOINT)
    assert response.status_code == 200, response.content

    json_data = response.json()

    assert len(json_data) == 5
    for i in range(5):
        for lang_code, _ in settings.LANGUAGES:
            assert "Example Venue" in json_data[i]["name"][lang_code]
            assert "Example Address" in json_data[i]["address"][lang_code]

    snapshot.assert_match(json_data)


@pytest.mark.django_db(reset_sequences=True)
def test_venue_retrieve_endpoint(
    project, settings, user_api_client, snapshot, django_assert_max_num_queries
):
    venue = VenueFactory(project=project)
    for lang_code, _ in settings.LANGUAGES:
        venue.set_current_language(lang_code)
        venue.name = f"Example Venue ({lang_code})"
        venue.address = f"Example Address ({lang_code})"
    venue.save()

    with django_assert_max_num_queries(5):
        response = user_api_client.get(f"{VENUES_ENDPOINT}{venue.id}/")
    assert response.status_code == 200, response.content

    json_data = response.json()

    for lang_code, _ in settings.LANGUAGES:
        assert f"Example Venue ({lang_code})" in json_data["name"][lang_code]
        assert f"Example Address ({lang_code})" in json_data["address"][lang_code]

    snapshot.assert_match(json_data)


@pytest.mark.django_db
def test_venues_endpoint_includes_system_venue(project, user_api_client):
    regular_venue = VenueFactory(project=project)
    system_venue = SystemVenueFactory()

    list_response = user_api_client.get(VENUES_ENDPOINT)
    assert list_response.status_code == 200
    list_ids = [v["id"] for v in list_response.json()]
    assert regular_venue.id in list_ids
    assert system_venue.id in list_ids

    detail_response = user_api_client.get(f"{VENUES_ENDPOINT}{system_venue.id}/")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == system_venue.id


@pytest.mark.django_db
def test_venues_endpoint_not_authenticated(user):
    response = APIClient().get(VENUES_ENDPOINT)
    assert response.status_code == 401
    venue = VenueFactory()
    response = APIClient().get(f"{VENUES_ENDPOINT}{venue.id}/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_venues_endpoint_no_permission(user_api_client):
    remove_perm(ACCESS_REPORT_API_PERM, user_api_client.user)
    response = user_api_client.get(VENUES_ENDPOINT)
    assert response.status_code == 403
    venue = VenueFactory()
    response = user_api_client.get(f"{VENUES_ENDPOINT}{venue.id}/")
    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    "override,expected_occ_children,expected_occ_adults",
    [
        (None, 2, 1),
        ((0, 0), 0, 0),
        ((4, 6), 4, 6),
    ],
)
def test_reports_attended_seats_and_override(
    project,
    user_api_client,
    django_assert_max_num_queries,
    override,
    expected_occ_children,
    expected_occ_adults,
):
    """
    Verify /reports/event/ and /reports/event-group/ return effective arrived
    participant counts (using occurrence overrides when set, without exposing
    override fields), expose enrolled_children_count / enrolled_adults_count,
    and expose attended_enrolment_count without increasing query count.
    """
    event_group = EventGroupFactory(project=project)
    event = EventFactory(
        project=project, event_group=event_group, capacity_per_occurrence=30
    )
    children_override, adults_override = override if override else (None, None)
    expected_occ_seats = expected_occ_children + expected_occ_adults
    expected_event_children = expected_occ_children + 1
    expected_event_adults = expected_occ_adults + 1
    expected_event_seats = expected_occ_seats + 2
    occ_overridable = OccurrenceFactory(
        event=event,
        time=timezone.now(),
        attended_children_count_override=children_override,
        attended_adults_count_override=adults_override,
    )
    occ_regular = OccurrenceFactory(event=event, time=timezone.now())

    EnrolmentFactory(
        occurrence=occ_overridable,
        extra_children_count=2,
        extra_guardians_count=1,
        attended=True,
        arrived_children_count=2,
        arrived_guardians_count=1,
    )
    EnrolmentFactory(
        occurrence=occ_regular,
        extra_children_count=0,
        extra_guardians_count=0,
        attended=True,
        arrived_children_count=1,
        arrived_guardians_count=1,
    )

    occ_overridable_time = timezone.localtime(occ_overridable.time).isoformat()
    occ_regular_time = timezone.localtime(occ_regular.time).isoformat()

    with django_assert_max_num_queries(7):
        event_res = user_api_client.get(EVENTS_ENDPOINT)
    assert event_res.status_code == 200
    event_data = event_res.json()[0]
    expected_occ_overridable = {
        "id": occ_overridable.id,
        "time": occ_overridable_time,
        "venue": {
            "url": f"http://testserver/reports/venue/{occ_overridable.venue_id}/",
            "id": occ_overridable.venue_id,
        },
        "enrolment_count": 1,
        "enrolled_children_count": 3,
        "enrolled_adults_count": 2,
        "attended_enrolment_count": 1,
        "attended_count": expected_occ_seats,
        "attended_children_count": expected_occ_children,
        "attended_adults_count": expected_occ_adults,
        "attended_seats": expected_occ_seats,
        "capacity": 30,
        "reserved_seats": 5,
    }
    expected_occ_regular = {
        "id": occ_regular.id,
        "time": occ_regular_time,
        "venue": {
            "url": f"http://testserver/reports/venue/{occ_regular.venue_id}/",
            "id": occ_regular.venue_id,
        },
        "enrolment_count": 1,
        "enrolled_children_count": 1,
        "enrolled_adults_count": 1,
        "attended_enrolment_count": 1,
        "attended_count": 2,
        "attended_children_count": 1,
        "attended_adults_count": 1,
        "attended_seats": 2,
        "capacity": 30,
        "reserved_seats": 2,
    }
    assert event_data == {
        "id": event.id,
        "name": event.name_with_translations,
        "project": {"id": project.id, "year": project.year},
        "event_group": {
            "url": f"http://testserver/reports/event-group/{event_group.id}/",
            "id": event_group.id,
        },
        "occurrences": [expected_occ_overridable, expected_occ_regular],
        "ticket_system": "internal",
        "occurrences_count": 2,
        "enrolment_count": 2,
        "enrolled_children_count": 4,
        "enrolled_adults_count": 3,
        "attended_enrolment_count": 2,
        "attended_count": expected_event_seats,
        "attended_children_count": expected_event_children,
        "attended_adults_count": expected_event_adults,
        "attended_seats": expected_event_seats,
        "capacity": 60,
        "reserved_seats": 7,
    }

    with django_assert_max_num_queries(7):
        group_res = user_api_client.get(f"{EVENT_GROUPS_ENDPOINT}{event_group.id}/")
    assert group_res.status_code == 200
    assert group_res.json() == {
        "url": f"http://testserver/reports/event-group/{event_group.id}/",
        "id": event_group.id,
        "name": event_group.name_with_translations,
        "project": {"id": project.id, "year": project.year},
        "events_count": 1,
        "enrolment_count": 2,
        "enrolled_children_count": 4,
        "enrolled_adults_count": 3,
        "attended_enrolment_count": 2,
        "attended_count": expected_event_seats,
        "attended_children_count": expected_event_children,
        "attended_adults_count": expected_event_adults,
        "attended_seats": expected_event_seats,
        "capacity": 60,
        "reserved_seats": 7,
    }

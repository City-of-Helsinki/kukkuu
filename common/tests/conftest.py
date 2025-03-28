import shutil
from datetime import timedelta

import factory.random
import pytest
import responses
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.utils import timezone, translation
from freezegun import freeze_time
from graphene.test import Client
from guardian.shortcuts import assign_perm

from children.factories import ChildWithGuardianFactory
from common.notification_service import SMSNotificationService
from events.factories import EventFactory, EventGroupFactory, OccurrenceFactory
from kukkuu.schema import schema
from kukkuu.views import SentryGraphQLView
from languages.models import Language
from projects.factories import ProjectFactory
from projects.models import (
    Project,
    ProjectPermission,
)
from users.factories import GuardianFactory, UserFactory
from users.models import User
from venues.factories import VenueFactory


@pytest.fixture(autouse=True)
def setup_test_environment(settings):
    factory.random.reseed_random("777")
    settings.DEFAULT_FROM_EMAIL = "kukkuu@example.com"
    settings.ILMOITIN_TRANSLATED_FROM_EMAIL = {}
    settings.MEDIA_ROOT = "test_media"
    settings.KUKKUU_HASHID_SALT = "topsecret"
    settings.KUKKUU_REMINDER_DAYS_IN_ADVANCE = 7
    settings.KUKKUU_DEFAULT_EVENT_DURATION = 120
    settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY = 30
    settings.OIDC_BROWSER_TEST_API_TOKEN_AUTH = {
        "ENABLED": False,
    }
    with translation.override("fi"), freeze_time("2020-12-12"):
        yield
    shutil.rmtree("test_media", ignore_errors=True)


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def future():
    return timezone.now() + timedelta(days=1)


@pytest.fixture
def past():
    return timezone.now() - timedelta(days=1)


@pytest.fixture
def languages():
    return [
        Language.objects.create_from_language_code(code)
        for code in ("fin", "swe", "eng")
    ] + [Language.objects.create_option_other()]


@pytest.fixture
def project():
    ProjectTranslation = apps.get_model("projects", "ProjectTranslation")
    project = Project.objects.get_or_create(year=2020)[0]
    project.translations.all().delete()
    ProjectTranslation.objects.create(
        master_id=project.pk,
        language_code="fi",
        name="Testiprojekti",
    )
    return project


@pytest.fixture
def another_project():
    return ProjectFactory(year=2030, name="Toinen testiprojekti")


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def api_client():
    return create_api_client_with_user(AnonymousUser())


@pytest.fixture
def user_api_client():
    return create_api_client_with_user(UserFactory())


@pytest.fixture
def guardian_api_client():
    return create_api_client_with_user(UserFactory(guardian=GuardianFactory()))


def _projects_user_api_client(
    projects: list[Project],
    permissions: list[ProjectPermission],
    global_permissions: list[ProjectPermission] | None = None,
) -> Client:
    """
    Create an API client with a random user with the given permissions
    in the given projects and the given, if any, global permissions.
    """
    user = UserFactory()
    for project in projects:
        for permission in permissions:
            assign_perm(permission.value, user, project)
    if global_permissions:
        for global_permission in global_permissions:
            assign_perm(global_permission.permission_name, user)
    return create_api_client_with_user(user)


@pytest.fixture()
def project_user_api_client(project):
    return _projects_user_api_client(
        [project], [ProjectPermission.ADMIN, ProjectPermission.VIEW_FAMILIES]
    )


@pytest.fixture
def project_user_with_global_view_families_perm_api_client(project):
    return _projects_user_api_client(
        [project],
        [ProjectPermission.ADMIN, ProjectPermission.VIEW_FAMILIES],
        [ProjectPermission.VIEW_FAMILIES],
    )


@pytest.fixture()
def project_user_no_view_families_perm_api_client(project):
    return _projects_user_api_client([project], [ProjectPermission.ADMIN])


@pytest.fixture(params=(False, True), ids=("object_perm", "model_perm"))
def publisher_api_client(request, project):
    user = UserFactory()
    assign_perm(ProjectPermission.ADMIN.value, user, project)

    if request.param:
        assign_perm(ProjectPermission.PUBLISH.value, user, project)
    else:
        assign_perm(ProjectPermission.PUBLISH.permission_name, user)

    return create_api_client_with_user(user)


@pytest.fixture(params=(False, True), ids=("object_perm", "model_perm"))
def event_group_manager_api_client(request, project):
    user = UserFactory()
    assign_perm(ProjectPermission.ADMIN.value, user, project)

    if request.param:
        assign_perm("manage_event_groups", user, project)
    else:
        assign_perm("projects.manage_event_groups", user)

    return create_api_client_with_user(user)


@pytest.fixture
def child_with_random_guardian(project):
    return ChildWithGuardianFactory(project=project)


@pytest.fixture
def child_with_user_guardian(guardian_api_client, project):
    return ChildWithGuardianFactory(
        relationship__guardian__user=guardian_api_client.user, project=project
    )


@pytest.fixture
def event(project):
    return EventFactory(published_at=timezone.now(), project=project)


@pytest.fixture
def unpublished_event(project):
    return EventFactory(project=project)


@pytest.fixture
def venue(project):
    return VenueFactory(project=project)


@pytest.fixture
def occurrence(venue, event):
    return OccurrenceFactory(time=timezone.now(), venue=venue, event=event)


@pytest.fixture
def unpublished_occurrence(venue, unpublished_event):
    return OccurrenceFactory(
        time=timezone.now() + timedelta(hours=6), venue=venue, event=unpublished_event
    )


@pytest.fixture
def event_group():
    return EventGroupFactory(published_at=timezone.now())


@pytest.fixture()
def wrong_project_api_client(another_project):
    return _projects_user_api_client([another_project], [ProjectPermission.ADMIN])


@pytest.fixture
def two_project_user_api_client(project, another_project):
    return _projects_user_api_client(
        [project, another_project],
        [ProjectPermission.ADMIN, ProjectPermission.VIEW_FAMILIES],
    )


@pytest.fixture(
    params=range(3), ids=["unauthenticated_user", "normal_user", "wrong_project_user"]
)
def unauthorized_user_api_client(
    api_client, user_api_client, wrong_project_api_client, request
):
    return (api_client, user_api_client, wrong_project_api_client)[request.param]


def create_api_client_with_user(user) -> Client:
    request = RequestFactory().post("/graphql")
    request.user = user
    client = Client(
        schema, context=request, format_error=SentryGraphQLView.format_error
    )
    client.user = user
    return client


@pytest.fixture
def sms_notification():
    return SMSNotificationService(
        api_token="topsecret", api_url="http://send-sms.test.localhost"
    )


@pytest.fixture
def mock_user_create_subscriptions_management_auth_token(monkeypatch):
    """
    Always return a fixed authorization verification token from
    ``User.create_subscriptions_management_auth_token()``.
    """
    original_func = User.create_subscriptions_management_auth_token

    def get_mocked_function(auth_key: str):
        def mocked_create_subscriptions_management_auth_token(self):
            auth_verification_token = original_func(self)
            auth_verification_token.key = auth_key
            auth_verification_token.save()
            return auth_verification_token

        return mocked_create_subscriptions_management_auth_token

    monkeypatch.setattr(
        User,
        "create_subscriptions_management_auth_token",
        get_mocked_function(auth_key="a1b2c3d4e5f6g7h8"),
    )


@pytest.fixture(params=["true", "True", "TRUE", "1", 1, True])
def true_value(request):
    return request.param


@pytest.fixture(params=["false", "False", "FALSE", "0", 0, False])
def false_value(request):
    return request.param

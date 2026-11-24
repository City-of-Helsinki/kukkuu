from unittest.mock import Mock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from organisations.factories import OrganisationFactory
from users.cache import UserRequestCache
from users.factories import UserFactory


@pytest.mark.django_db
def test_user_request_cache_get_organisation_ids_and_invalidate(
    django_assert_num_queries,
):
    org_1 = OrganisationFactory(name="Org 1")
    org_2 = OrganisationFactory(name="Org 2")
    user = UserFactory()
    user.organisations.add(org_1, org_2)

    request = RequestFactory().get("/")
    request.user = user

    with django_assert_num_queries(1):
        org_ids = UserRequestCache.get_organisation_ids(request)
    assert org_ids == frozenset({org_1.id, org_2.id})

    # Subsequent calls on the same request do not hit the database
    with django_assert_num_queries(0):
        cached_ids = UserRequestCache.get_organisation_ids(request)
    assert cached_ids is org_ids

    # Invalidating forces a fresh lookup on the next call
    UserRequestCache.invalidate(request)
    with django_assert_num_queries(1):
        refetched_ids = UserRequestCache.get_organisation_ids(request)
    assert refetched_ids == frozenset({org_1.id, org_2.id})


@pytest.mark.django_db
def test_user_request_cache_extracts_context_from_info(django_assert_num_queries):
    org = OrganisationFactory(name="Info Org")
    user = UserFactory()
    user.organisations.add(org)

    request = RequestFactory().get("/")
    request.user = user
    info = Mock(context=request)

    org_ids = UserRequestCache.get_organisation_ids(info)
    assert org_ids == frozenset({org.id})

    with django_assert_num_queries(0):
        assert UserRequestCache.get_organisation_ids(request) is org_ids

    UserRequestCache.invalidate(info)
    assert not hasattr(request, UserRequestCache.ORGANISATION_IDS_ATTR)


@pytest.mark.django_db
def test_user_request_cache_is_not_shared_between_requests(django_assert_num_queries):
    org = OrganisationFactory(name="Isolated Org")
    user = UserFactory()
    user.organisations.add(org)

    request_a = RequestFactory().get("/")
    request_a.user = user
    request_b = RequestFactory().get("/")
    request_b.user = user

    UserRequestCache.get_organisation_ids(request_a)
    assert hasattr(request_a, UserRequestCache.ORGANISATION_IDS_ATTR)
    assert not hasattr(request_b, UserRequestCache.ORGANISATION_IDS_ATTR)


@pytest.mark.django_db
def test_user_request_cache_returns_none_for_anonymous_and_sysadmin(
    django_assert_num_queries,
):
    anon_request = RequestFactory().get("/")
    anon_request.user = AnonymousUser()

    sysadmin = UserFactory(is_staff=True)
    sysadmin_request = RequestFactory().get("/")
    sysadmin_request.user = sysadmin

    with django_assert_num_queries(0):
        assert UserRequestCache.get_organisation_ids(anon_request) is None
        assert UserRequestCache.get_organisation_ids(sysadmin_request) is None

from unittest.mock import Mock

import pytest
from django.test import RequestFactory
from graphql_relay import to_global_id

from children.cache import ChildRequestCache
from children.factories import ChildWithGuardianFactory
from kukkuu.exceptions import ObjectDoesNotExistError


@pytest.mark.django_db
def test_child_request_cache_get_set_and_invalidate(project):
    request = RequestFactory().get("/")
    child = ChildWithGuardianFactory(project=project)

    assert ChildRequestCache.get(request, child.id) is None

    ChildRequestCache.set(request, child)
    assert ChildRequestCache.get(request, child.id) == child
    assert ChildRequestCache.get(request, str(child.id)) == child

    ChildRequestCache.invalidate(request, child.id)
    assert ChildRequestCache.get(request, child.id) is None


@pytest.mark.django_db
def test_child_request_cache_get_or_fetch(project, django_assert_num_queries):
    child = ChildWithGuardianFactory(project=project)
    user = child.guardians.first().user
    request = RequestFactory().get("/")
    request.user = user

    child_gid = to_global_id("ChildNode", child.id)

    # First call fetches and caches
    cached_child = ChildRequestCache.get_or_fetch(request, child_gid)
    assert cached_child.id == child.id

    # Second call should not hit the database
    with django_assert_num_queries(0):
        again = ChildRequestCache.get_or_fetch(request, child_gid)
        assert again is cached_child


@pytest.mark.django_db
def test_child_request_cache_extracts_context_from_info(project):
    child = ChildWithGuardianFactory(project=project)
    user = child.guardians.first().user
    request = RequestFactory().get("/")
    request.user = user
    info = Mock(context=request)

    child_gid = to_global_id("ChildNode", child.id)
    cached_child = ChildRequestCache.get_or_fetch(info, child_gid)
    assert cached_child.id == child.id
    assert ChildRequestCache.get(request, child.id) == cached_child

    ChildRequestCache.invalidate(info, child.id)
    assert ChildRequestCache.get(request, child.id) is None


@pytest.mark.django_db
def test_child_request_cache_is_not_shared_between_requests(project):
    child = ChildWithGuardianFactory(project=project)
    user = child.guardians.first().user
    child_gid = to_global_id("ChildNode", child.id)
    # Same user on both requests, so only the request can separate the caches
    request_a = RequestFactory().get("/")
    request_a.user = user
    request_b = RequestFactory().get("/")
    request_b.user = user
    cached_child = ChildRequestCache.get_or_fetch(request_a, child_gid)
    assert ChildRequestCache.get(request_a, child.id) == cached_child
    assert ChildRequestCache.get(request_b, child.id) is None


@pytest.mark.django_db
def test_child_request_cache_permission_denied(project, user):
    child = ChildWithGuardianFactory(project=project)
    request = RequestFactory().get("/")
    request.user = user  # User has no relationship with child

    child_gid = to_global_id("ChildNode", child.id)
    with pytest.raises(ObjectDoesNotExistError):
        ChildRequestCache.get_or_fetch(request, child_gid)
    assert ChildRequestCache.get(request, child.id) is None


def test_child_request_cache_invalid_id():
    request = RequestFactory().get("/")
    request.user = Mock()
    with pytest.raises(ObjectDoesNotExistError):
        ChildRequestCache.get_or_fetch(request, "invalid-global-id")

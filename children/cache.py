import uuid
from typing import Optional

from django.core.exceptions import ValidationError

from children.models import Child
from common.utils import get_node_id_from_global_id
from kukkuu.exceptions import ObjectDoesNotExistError


class ChildRequestCache:
    """
    Request-scoped cache for Child instances to eliminate N+1 queries during
    GraphQL execution (filters and field resolvers).

    In GraphQL queries (e.g. events search), multiple field resolvers (such as
    `canChildEnroll`, `enrolmentDeniedReason`, and `childPassword`) as well as
    `EventFilter` inspect the same child. Caching the prefetched Child instance
    on the request context guarantees that the child and its relations are
    fetched at most once per request.
    """

    CACHE_ATTR = "_child_cache"

    @classmethod
    def _extract_context(cls, context_or_info):
        """Extract the underlying HttpRequest or request context object."""
        return getattr(context_or_info, "context", context_or_info)

    @classmethod
    def _get_cache(cls, context_or_info) -> dict[str, Child]:
        """Return the child cache dictionary stored on the request context."""
        context = cls._extract_context(context_or_info)
        cache = getattr(context, cls.CACHE_ATTR, None)
        if cache is None:
            cache = {}
            setattr(context, cls.CACHE_ATTR, cache)
        return cache

    @classmethod
    def get(cls, context_or_info, child_id: str | uuid.UUID) -> Optional[Child]:
        """Retrieve a cached Child by ID from the request cache."""
        return cls._get_cache(context_or_info).get(str(child_id))

    @classmethod
    def set(cls, context_or_info, child: Child) -> None:
        """Store a Child instance in the request cache."""
        cls._get_cache(context_or_info)[str(child.id)] = child

    @classmethod
    def invalidate(cls, context_or_info, child_id: str | uuid.UUID) -> None:
        """
        Evict a Child instance from the request cache by primary key.
        Typically called after mutations that modify the child's enrolments
        or passwords.
        """
        cls._get_cache(context_or_info).pop(str(child_id), None)

    @classmethod
    def get_or_fetch(cls, context_or_info, child_global_id: str) -> Child:
        """
        Retrieve a Child instance from cache or fetch with eager prefetching.

        1. Checks request cache by decoded ChildNode PK.
        2. Permission check: Filters by `Child.objects.user_can_view(context.user)`.
        3. Eager prefetching: Prefetches `project`, `occurrences__event`, and
           `ticket_system_passwords__event`.
        4. Memoizes on `context._child_cache`.

        :param context_or_info: Django HttpRequest or GraphQL ResolveInfo.
        :param child_global_id: Relay global ID (base64-encoded `ChildNode:<pk>`).
        :return: Prefetched Child instance.
        :raises ObjectDoesNotExistError: If child ID is invalid, child is not found,
            or user lacks view permission.
        """
        context = cls._extract_context(context_or_info)
        child_id = get_node_id_from_global_id(child_global_id, "ChildNode")
        if not child_id:
            raise ObjectDoesNotExistError(
                Child.DoesNotExist("Child matching query does not exist.")
            )

        cache = cls._get_cache(context)
        if child_id in cache:
            return cache[child_id]

        try:
            child = (
                Child.objects.user_can_view(context.user)
                .select_related("project")
                .prefetch_related(
                    "occurrences__event",
                    "ticket_system_passwords__event",
                )
                .get(id=child_id)
            )
        except (Child.DoesNotExist, ValidationError, ValueError) as e:
            raise ObjectDoesNotExistError(e)

        cache[str(child.id)] = child
        return child

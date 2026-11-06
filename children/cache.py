import uuid
from typing import Any, Optional

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
    def _extract_context(cls, context_or_info: Any) -> Any:
        """Extract the underlying HttpRequest or request context object."""
        return getattr(context_or_info, "context", context_or_info)

    @classmethod
    def _canonicalize_id(cls, child_id: Any) -> str:
        """
        Normalize a child ID into a standard lowercase UUID string with hyphens.

        Handles UUID instances, strings with or without hyphens, mixed case, and
        whitespace. Falls back to stripped string representation for non-UUID keys.
        """
        if child_id is None:
            return ""
        if isinstance(child_id, uuid.UUID):
            return str(child_id)
        raw_str = str(child_id).strip()
        try:
            return str(uuid.UUID(raw_str))
        except (ValueError, AttributeError):
            return raw_str

    @classmethod
    def _get_user_key(cls, user: Any) -> str:
        """
        Generate a unique cache partition key for the given user.

        Ensures cache entries are strictly scoped to the viewing user so that
        access permissions are never bypassed across user boundaries.
        """
        if user is None:
            return "anon"
        if hasattr(user, "is_authenticated") and not user.is_authenticated:
            return "anon"
        if hasattr(user, "pk") and user.pk is not None:
            return f"user:{user.pk}"
        if hasattr(user, "id") and user.id is not None:
            return f"user:{user.id}"
        if hasattr(user, "uuid") and user.uuid is not None:
            return f"user:{user.uuid}"
        return f"user:{id(user)}"

    @classmethod
    def _get_cache_dict(
        cls, context_or_info: Any, user: Any = None
    ) -> Optional[dict[str, Child]]:
        """
        Return the child cache dictionary for the specified user on the context.

        The root cache on the context partitions child entries by user key,
        guaranteeing that different users sharing the same context cannot see
        or resolve each other's cached child snapshots.
        """
        context = cls._extract_context(context_or_info)
        if context is None:
            return None
        if user is None and hasattr(context, "user"):
            user = context.user
        user_key = cls._get_user_key(user)
        if not hasattr(context, cls.CACHE_ATTR):
            setattr(context, cls.CACHE_ATTR, {})
        root_cache = getattr(context, cls.CACHE_ATTR)
        if not isinstance(root_cache, dict):
            root_cache = {}
            setattr(context, cls.CACHE_ATTR, root_cache)
        return root_cache.setdefault(user_key, {})

    @classmethod
    def get(
        cls,
        context_or_info: Any,
        child_id: int | str | uuid.UUID,
        user: Any = None,
    ) -> Optional[Child]:
        """
        Retrieve a cached Child by primary key or string representation of PK.
        """
        cache = cls._get_cache_dict(context_or_info, user)
        if cache is None:
            return None
        key = cls._canonicalize_id(child_id)
        return cache.get(key) if key else None

    @classmethod
    def set(cls, context_or_info: Any, child: Child, user: Any = None) -> None:
        """
        Store a Child instance in the request context cache.
        """
        if child is None or child.id is None:
            return
        key = cls._canonicalize_id(child.id)
        if not key:
            return
        cache = cls._get_cache_dict(context_or_info, user)
        if cache is not None:
            cache[key] = child

    @classmethod
    def invalidate(
        cls,
        context_or_info: Any,
        child_id: int | str | uuid.UUID,
        user: Any = None,
    ) -> None:
        """
        Evict a Child instance from the request cache by primary key.
        Typically called after mutations that modify the child's enrolments
        or passwords.
        """
        context = cls._extract_context(context_or_info)
        if context is None or not hasattr(context, cls.CACHE_ATTR):
            return
        key = cls._canonicalize_id(child_id)
        if not key:
            return
        root_cache = getattr(context, cls.CACHE_ATTR)
        if not isinstance(root_cache, dict):
            return
        if user is not None:
            user_key = cls._get_user_key(user)
            if user_key in root_cache and isinstance(root_cache[user_key], dict):
                root_cache[user_key].pop(key, None)
        else:
            for user_cache in root_cache.values():
                if isinstance(user_cache, dict):
                    user_cache.pop(key, None)

    @classmethod
    def get_or_fetch(
        cls,
        context_or_info: Any,
        child_global_id: str,
        user: Any = None,
    ) -> Child:
        """
        Retrieve a Child instance from cache or fetch with eager prefetching.

        Key behaviors:
        1. Checks request cache by decoded, canonicalized PK scoped to the user.
        2. Permission check: Filters by `Child.objects.user_can_view(user)`.
        3. Eager prefetching: Prefetches `project`, `occurrences__event`, and
           `ticket_system_passwords__event`. This allows methods on `Child` like
           `can_child_enroll()`, `get_enrolled_event_ids()`, `get_enrolment_count()`,
           and `get_ticket_system_passwords_by_event_id()` to run in memory without
           additional SQL queries.
        4. Memoizes on `context._child_cache` under the authorized user's partition.

        :param context_or_info: Django HttpRequest or GraphQL ResolveInfo.
        :param child_global_id: Relay global ID (base64-encoded `ChildNode:<pk>`).
        :param user: Optional User instance; defaults to `context.user`.
        :return: Prefetched Child instance.
        :raises ObjectDoesNotExistError: If child ID is invalid, child is not found,
            or user lacks view permission.
        """
        context = cls._extract_context(context_or_info)
        if user is None and hasattr(context, "user"):
            user = context.user

        raw_id = get_node_id_from_global_id(child_global_id, "ChildNode")
        canonical_id = cls._canonicalize_id(raw_id)

        cache = cls._get_cache_dict(context, user)
        if cache is not None and canonical_id and canonical_id in cache:
            return cache[canonical_id]

        try:
            if not canonical_id:
                raise Child.DoesNotExist("Child matching query does not exist.")
            child = (
                Child.objects.user_can_view(user)
                .select_related("project")
                .prefetch_related(
                    "occurrences__event",
                    "ticket_system_passwords__event",
                )
                .get(id=canonical_id)
            )
        except (Child.DoesNotExist, ValidationError, ValueError) as e:
            raise ObjectDoesNotExistError(e)

        if cache is not None and canonical_id:
            cache[canonical_id] = child

        return child

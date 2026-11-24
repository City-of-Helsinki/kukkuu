import uuid
from typing import Optional


class UserRequestCache:
    """
    Request-scoped cache for user-related permission data (such as the user's
    organisation IDs) to eliminate N+1 queries during GraphQL execution.

    When resolving permission-checked fields across many Event or Occurrence
    nodes in a single GraphQL request (e.g. `canUserAdminister` on EventNode or
    protected arrival/override metrics on OccurrenceNode), caching the user's
    organisation IDs on the request context ensures the user's organisation
    memberships are queried at most once per request.
    """

    ORGANISATION_IDS_ATTR = "_user_organisation_ids"

    @classmethod
    def _extract_context(cls, context_or_info):
        """Extract the underlying HttpRequest or request context object."""
        return getattr(context_or_info, "context", context_or_info)

    @classmethod
    def get_organisation_ids(cls, context_or_info) -> Optional[frozenset[uuid.UUID]]:
        """
        Return the memoised frozenset of organisation IDs for the request's user,
        or None if the user is anonymous or a system administrator (who can
        administer all organisations without an organisation membership query).
        """
        context = cls._extract_context(context_or_info)
        if not hasattr(context, cls.ORGANISATION_IDS_ATTR):
            user = getattr(context, "user", None)
            organisation_ids = (
                frozenset(user.organisations.values_list("id", flat=True))
                if user and user.is_authenticated and not user.is_system_administrator
                else None
            )
            setattr(context, cls.ORGANISATION_IDS_ATTR, organisation_ids)
        return getattr(context, cls.ORGANISATION_IDS_ATTR)

    @classmethod
    def invalidate(cls, context_or_info) -> None:
        """Evict cached user organisation IDs from the request context."""
        context = cls._extract_context(context_or_info)
        if hasattr(context, cls.ORGANISATION_IDS_ATTR):
            delattr(context, cls.ORGANISATION_IDS_ATTR)

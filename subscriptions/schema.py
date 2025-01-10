import logging

import graphene
from django.core.exceptions import ValidationError
from graphene import relay
from graphene_django import DjangoObjectType

from children.models import Child
from children.schema import ChildNode
from common.utils import (
    get_node_id_from_global_id,
    login_required,
    map_enums_to_values_in_kwargs,
)
from events.models import Occurrence
from events.schema import OccurrenceNode
from hel_django_auditlog_extra.graphene_decorators import auditlog_access
from kukkuu.consts import OCCURRENCE_IS_NOT_FULL_ERROR
from kukkuu.exceptions import (
    AlreadySubscribedError,
    ObjectDoesNotExistError,
    OccurrenceIsNotFullError,
)
from subscriptions.models import FreeSpotNotificationSubscription
from users.schema import GuardianNode
from verification_tokens.decorators import user_from_auth_verification_token

logger = logging.getLogger(__name__)


@auditlog_access
class FreeSpotNotificationSubscriptionNode(DjangoObjectType):
    occurrence = graphene.Field(OccurrenceNode)  # WORKAROUND: See resolve_occurrence

    class Meta:
        model = FreeSpotNotificationSubscription
        interfaces = (relay.Node,)
        fields = ("id", "created_at", "child")
        filter_fields = ("child_id", "occurrence_id")

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info).user_can_view(info.context.user)

    def resolve_occurrence(self, info, **kwargs):
        """
        Resolver for the occurrence field, which is a foreign key.

        WORKAROUND: Just putting "occurrence" into Meta.fields breaks
        occurrence field resolving in test_child_free_spot_notifications_query
        with graphene-django 3.2.2, but works with graphene-django 3.1.3.

        Probably caused by the changes done after 3.1.3:
        - "fix: fk resolver permissions leak":
          - https://github.com/graphql-python/graphene-django/pull/1411
        - "fix: foreign key nullable and custom resolver":
          - https://github.com/graphql-python/graphene-django/pull/1446

        Found a similar graphene-django issue #1482:
        - "Vesion 3.1.5 returns null for an object pointed to non PK in referred table":
          - https://github.com/graphql-python/graphene-django/issues/1482
        """
        return self.occurrence


def validate_free_spot_notification_subscription(child, occurrence):
    if child.free_spot_notification_subscriptions.filter(
        occurrence=occurrence
    ).exists():
        raise AlreadySubscribedError(
            "Child already subscribed to free spot notifications of this occurrence"
        )
    try:
        FreeSpotNotificationSubscription(child=child, occurrence=occurrence).clean()
    except ValidationError as e:
        if e.code == OCCURRENCE_IS_NOT_FULL_ERROR:
            raise OccurrenceIsNotFullError(e.message)


def _get_child_and_occurrence(info, **kwargs):
    occurrence_id = get_node_id_from_global_id(
        kwargs["occurrence_id"], "OccurrenceNode"
    )
    child_id = get_node_id_from_global_id(kwargs["child_id"], "ChildNode")
    user = info.context.user
    try:
        child = Child.objects.user_can_update(user).get(pk=child_id)
    except Child.DoesNotExist as e:
        raise ObjectDoesNotExistError(e)

    try:
        occurrence = Occurrence.objects.filter(event__project=child.project).get(
            pk=occurrence_id
        )
    except Occurrence.DoesNotExist as e:
        raise ObjectDoesNotExistError(e)

    return child, occurrence


class SubscribeToFreeSpotNotificationMutation(graphene.relay.ClientIDMutation):
    class Input:
        occurrence_id = graphene.GlobalID()
        child_id = graphene.GlobalID()

    occurrence = graphene.Field(OccurrenceNode)
    child = graphene.Field(ChildNode)

    @classmethod
    @login_required
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user
        child, occurrence = _get_child_and_occurrence(info, **kwargs)

        validate_free_spot_notification_subscription(child, occurrence)

        FreeSpotNotificationSubscription.objects.create(
            child=child, occurrence=occurrence
        )

        logger.info(
            f"User {user.uuid} subscribed child {child.pk} to occurrence "
            f"{occurrence} free spot notification."
        )

        return SubscribeToFreeSpotNotificationMutation(
            child=child, occurrence=occurrence
        )


class UnsubscribeFromFreeSpotNotificationMutation(graphene.relay.ClientIDMutation):
    class Input:
        occurrence_id = graphene.GlobalID()
        child_id = graphene.GlobalID()

    occurrence = graphene.Field(OccurrenceNode)
    child = graphene.Field(ChildNode)

    @classmethod
    @login_required
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user
        child, occurrence = _get_child_and_occurrence(info, **kwargs)

        try:
            subscription = FreeSpotNotificationSubscription.objects.get(
                child=child, occurrence=occurrence
            )
        except FreeSpotNotificationSubscription.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

        subscription.delete()

        logger.info(
            f"User {user.uuid} unsubscribed child {child.pk} from occurrence "
            f"{occurrence} free spot notification."
        )

        return UnsubscribeFromFreeSpotNotificationMutation(
            child=child, occurrence=occurrence
        )


class UnsubscribeFromAllNotificationsMutation(graphene.relay.ClientIDMutation):
    """
    Unsubscribe user from all the notifications.

    NOTE: This mutation deletes the user's FreeSpotNotifications,
    which are linked to a Child and Occurrence instances.
    **It should be noted that the current model architecture allows
    that a child can have multiple guardians, so unsubscribe can delete
    some notifications from other users as well. However, the UI apps
    has never allowed more than 1 guardian for a child.**
    """

    class Input:
        auth_token = graphene.String(
            description="Auth token can be used to authorize the action "
            "without logging in as a user."
        )

    guardian = graphene.Field(GuardianNode)
    unsubscribed = graphene.Boolean()

    @classmethod
    # When the login_required raises a PermissionDenied exception,
    # use the auth_token from the input variables
    # to populate the context.user with the token related user
    # and then try again.
    @user_from_auth_verification_token(
        get_token=lambda variables: variables.get("auth_token", None),
        use_only_when_first_denied=True,
    )
    @login_required
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user
        user.unsubscribe_all_notification_subscriptions()
        logger.info(f"User {user.uuid} unsubscribed from all notifications.")
        return UnsubscribeFromAllNotificationsMutation(
            guardian=user.guardian, unsubscribed=True
        )


class Mutation:
    subscribe_to_free_spot_notification = (
        SubscribeToFreeSpotNotificationMutation.Field()
    )
    unsubscribe_from_free_spot_notification = (
        UnsubscribeFromFreeSpotNotificationMutation.Field()
    )
    unsubscribe_from_all_notifications = UnsubscribeFromAllNotificationsMutation.Field()

import logging

import graphene
from django.core.exceptions import ValidationError
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from children.models import Child
from children.schema import ChildNode
from common.utils import get_node_id_from_global_id
from events.models import Occurrence
from events.schema import OccurrenceNode
from kukkuu.consts import OCCURRENCE_IS_NOT_FULL_ERROR
from kukkuu.exceptions import (
    AlreadySubscribedError,
    ObjectDoesNotExistError,
    OccurrenceIsNotFullError,
)
from subscriptions.models import FreeSpotNotificationSubscription

logger = logging.getLogger(__name__)


class FreeSpotNotificationSubscriptionNode(DjangoObjectType):
    class Meta:
        model = FreeSpotNotificationSubscription
        interfaces = (relay.Node,)
        fields = ("id", "created_at", "child", "occurrence")
        filter_fields = ("child_id", "occurrence_id")

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info).user_can_view(info.context.user)


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
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user
        child, occurrence = _get_child_and_occurrence(info, **kwargs)

        validate_free_spot_notification_subscription(child, occurrence)

        FreeSpotNotificationSubscription.objects.create(
            child=child, occurrence=occurrence
        )

        logger.info(
            f"user {user.uuid} subscribed child {child.pk} to occurrence "
            f"{occurrence} free spot notification"
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
            f"user {user.uuid} unsubscribed child {child.pk} from occurrence "
            f"{occurrence} free spot notification"
        )

        return UnsubscribeFromFreeSpotNotificationMutation(
            child=child, occurrence=occurrence
        )


class Mutation:
    subscribe_to_free_spot_notification = (
        SubscribeToFreeSpotNotificationMutation.Field()
    )
    unsubscribe_from_free_spot_notification = (
        UnsubscribeFromFreeSpotNotificationMutation.Field()
    )

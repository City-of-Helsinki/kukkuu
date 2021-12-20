import logging
from copy import deepcopy

import graphene
from django.apps import apps
from django.db import transaction
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from common.schema import LanguageEnum
from common.utils import (
    get_obj_if_user_can_administer,
    project_user_required,
    update_object_with_translations,
)
from events.models import Event, Occurrence
from kukkuu.exceptions import DataValidationError, MessageAlreadySentError
from projects.models import Project

from .models import AlreadySentError, Message

logger = logging.getLogger(__name__)

MessageTranslation = apps.get_model("messaging", "MessageTranslation")


class MessageTranslationType(DjangoObjectType):
    class Meta:
        model = MessageTranslation
        exclude = ("id", "master")


class RecipientSelectionEnum(graphene.Enum):
    ALL = "all"
    INVITED = "invited"
    ENROLLED = "enrolled"
    ATTENDED = "attended"
    SUBSCRIBED_TO_FREE_SPOT_NOTIFICATION = "subscribed_to_free_spot_notification"


class MessageNode(DjangoObjectType):
    subject = graphene.String()
    body_text = graphene.String()
    recipient_selection = graphene.Field(RecipientSelectionEnum)

    class Meta:
        model = Message
        interfaces = (relay.Node,)
        fields = (
            "id",
            "project",
            "created_at",
            "updated_at",
            "subject",
            "body_text",
            "recipient_selection",
            "event",
            "occurrences",
            "sent_at",
            "recipient_count",
            "translations",
        )
        filter_fields = ("project_id",)

    @classmethod
    @project_user_required
    def get_queryset(cls, queryset, info):
        return queryset.user_can_view(info.context.user).prefetch_related(
            "translations"
        )

    @classmethod
    @project_user_required
    def get_node(cls, info, id):
        try:
            return (
                cls._meta.model.objects.user_can_view(info.context.user)
                .prefetch_related("translations")
                .get(id=id)
            )
        except cls._meta.model.DoesNotExist:
            return None

    def resolve_recipient_count(self, info, **kwargs):
        return self.get_recipient_count()


class MessageTranslationsInput(graphene.InputObjectType):
    language_code = LanguageEnum(required=True)
    subject = graphene.String()
    body_text = graphene.String()


class AddMessageMutation(graphene.relay.ClientIDMutation):
    class Input:
        translations = graphene.List(MessageTranslationsInput)
        project_id = graphene.GlobalID()
        recipient_selection = RecipientSelectionEnum(required=True)
        event_id = graphene.ID()
        occurrence_ids = graphene.List(graphene.NonNull(graphene.ID))

    message = graphene.Field(MessageNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        data = deepcopy(kwargs)

        data["project"] = get_obj_if_user_can_administer(
            info, data.pop("project_id"), Project
        )

        event_id = data.pop("event_id", None)
        if event_id:
            data["event"] = get_obj_if_user_can_administer(info, event_id, Event)
        else:
            data["event"] = None
        occurrences = [
            get_obj_if_user_can_administer(info, occurrence_id, Occurrence)
            for occurrence_id in data.pop("occurrence_ids", [])
        ]

        validate_recipient_selection_and_data(
            data["recipient_selection"], data["event"], occurrences
        )
        validate_event_and_occurrences(data["event"], occurrences)

        message = Message.objects.create_translatable_object(**data)
        if occurrences:
            message.occurrences.set(occurrences)

        logger.info(
            f"user {info.context.user.uuid} added message {message} with data {kwargs}"
        )

        return AddMessageMutation(message=message)


class UpdateMessageMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()
        translations = graphene.List(MessageTranslationsInput)
        project_id = graphene.ID()
        recipient_selection = RecipientSelectionEnum()
        event_id = graphene.ID()
        occurrence_ids = graphene.List(graphene.NonNull(graphene.ID))

    message = graphene.Field(MessageNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        data = deepcopy(kwargs)
        message = get_obj_if_user_can_administer(info, data.pop("id"), Message)

        if message.sent_at:
            raise MessageAlreadySentError(
                "Cannot update because the message has already been sent."
            )

        if "project_id" in data:
            data["project_id"] = get_obj_if_user_can_administer(
                info, data.pop("project_id"), Project
            )

        if "event_id" in data:
            event_id = data.pop("event_id")
            data["event"] = (
                get_obj_if_user_can_administer(info, event_id, Event)
                if event_id
                else None
            )
        if "occurrence_ids" in data:
            occurrences = [
                get_obj_if_user_can_administer(info, occurrence_id, Occurrence)
                for occurrence_id in data.pop("occurrence_ids", [])
            ]
        else:
            occurrences = None

        if recipient_selection := data.get("recipient_selection"):
            validate_recipient_selection_and_data(
                recipient_selection,
                data["event"] if "event" in data else message.event,
                occurrences,
            )
        validate_event_and_occurrences(
            data["event"] if "event" in data else message.event,
            occurrences if occurrences is not None else message.occurrences.all(),
        )

        update_object_with_translations(message, data)

        if occurrences is not None:
            message.occurrences.set(occurrences)

        logger.info(
            f"user {info.context.user.uuid} updated message {message} with data {kwargs}"  # noqa: E501
        )

        return UpdateMessageMutation(message=message)


def validate_recipient_selection_and_data(recipient_selection, event, occurrences):
    if recipient_selection == RecipientSelectionEnum.INVITED and (event or occurrences):
        raise DataValidationError(
            "Selecting an event or occurrences are not supported when "
            "recipient_selection is INVITED."
        )


def validate_event_and_occurrences(event, occurrences):
    if not occurrences:
        return

    if not event:
        raise DataValidationError("Event is needed when there are occurrences.")

    if any(occurrence.event != event for occurrence in occurrences):
        raise DataValidationError("All of the occurrences do not belong to the event.")


class SendMessageMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    message = graphene.Field(MessageNode)

    @classmethod
    @project_user_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        message = get_obj_if_user_can_administer(info, kwargs["id"], Message)

        try:
            message.send()
        except AlreadySentError:
            raise MessageAlreadySentError(
                "Cannot send because the message has already been sent."
            )

        logger.info(f"user {info.context.user.uuid} sent message {message}")

        return SendMessageMutation(message=message)


class DeleteMessageMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    @classmethod
    @project_user_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        message = get_obj_if_user_can_administer(info, kwargs["id"], Message)
        if message.sent_at:
            raise MessageAlreadySentError(
                "Cannot delete because the message has already been sent."
            )

        log_text = f"user {info.context.user.uuid} deleted message {message}"
        message.delete()

        logger.info(log_text)

        return DeleteMessageMutation()


class Query:
    message = relay.Node.Field(MessageNode)
    messages = DjangoFilterConnectionField(MessageNode)


class Mutation:
    add_message = AddMessageMutation.Field()
    update_message = UpdateMessageMutation.Field()
    send_message = SendMessageMutation.Field()
    delete_message = DeleteMessageMutation.Field()

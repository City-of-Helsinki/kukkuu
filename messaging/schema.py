import logging
from copy import deepcopy
from typing import List, Optional

import django_filters
import graphene
from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.db import transaction
from graphene import relay
from graphene_django import DjangoObjectType

from common.schema import DjangoFilterAndOffsetConnectionField, LanguageEnum
from common.utils import (
    get_node_id_from_global_id,
    get_obj_if_user_can_administer,
    map_enums_to_values_in_kwargs,
    project_user_required,
    update_object_with_translations,
)
from events.models import Event, Occurrence
from hel_django_auditlog_extra.graphene_decorators import auditlog_access
from kukkuu.exceptions import DataValidationError, MessageAlreadySentError
from projects.models import Project
from users.models import User

from .exceptions import AlreadySentError
from .models import Message

logger = logging.getLogger(__name__)

MessageTranslation = apps.get_model("messaging", "MessageTranslation")


class MessageTranslationType(DjangoObjectType):
    class Meta:
        model = MessageTranslation
        exclude = ("id", "master")


class RecipientSelectionEnum(graphene.Enum):
    ALL = Message.ALL
    INVITED = Message.INVITED
    ENROLLED = Message.ENROLLED
    ATTENDED = Message.ATTENDED
    SUBSCRIBED_TO_FREE_SPOT_NOTIFICATION = Message.SUBSCRIBED_TO_FREE_SPOT_NOTIFICATION


ProtocolType = graphene.Enum(
    "ProtocolType", [(c[0].upper(), c[0]) for c in Message.PROTOCOL_CHOICES]
)


class MessagesConnection(graphene.Connection):
    class Meta:
        abstract = True

    count = graphene.Int(required=True)

    def resolve_count(self, info, **kwargs):
        return self.length


class MessageFilter(django_filters.FilterSet):
    occurrences = django_filters.ModelMultipleChoiceFilter(
        queryset=Occurrence.objects.all(),
        conjoined=False,
        method="filter_occurrences",
        label="Occurrences",
        help_text="Filter by multiple occurrences.",
    )

    order_by = django_filters.OrderingFilter(fields=("created_at", "sent_at"))

    def __init__(self, data=None, *args, **kwargs):
        """
        Initializes the MessageFilter instance and processes occurrence global IDs.

        Args:
            data (dict, optional): The filter data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        if data:
            data = self._fix_occurrences_global_ids(data)
        super().__init__(data, *args, **kwargs)

    class Meta:
        model = Message
        fields = ["project_id", "protocol", "occurrences"]

    def filter_occurrences(self, qs, name, value):
        if value:
            return qs.filter(occurrences__in=value)
        return qs

    def _fix_occurrences_global_ids(self, data):
        """
        Extracts and converts occurrence global IDs to their corresponding node IDs.

        Args:
            data (dict): The filter data containing the 'occurrences' key.

        Returns:
            dict: The updated filter data with 'occurrences'
            replaced by a list of global node IDs.
        """
        value = data.pop("occurrences", None)
        occurrences_node_ids = None
        occurrences_ids = None

        if isinstance(value, (list, tuple)):
            occurrences_node_ids = value
        elif isinstance(value, str):
            occurrences_node_ids = [value]

        if occurrences_node_ids:
            occurrences_ids = [
                get_node_id_from_global_id(node_id, "OccurrenceNode")
                for node_id in occurrences_node_ids
            ]

        return {**data, "occurrences": occurrences_ids}


@auditlog_access
class MessageNode(DjangoObjectType):
    subject = graphene.String()
    body_text = graphene.String()
    recipient_selection = graphene.Field(RecipientSelectionEnum)

    class Meta:
        model = Message
        interfaces = (relay.Node,)
        connection_class = MessagesConnection
        fields = (
            "id",
            "project",
            "protocol",
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
        filterset_class = MessageFilter

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
        protocol = ProtocolType(default=Message.EMAIL, required=True)
        translations = graphene.List(MessageTranslationsInput)
        project_id = graphene.GlobalID()
        recipient_selection = RecipientSelectionEnum(
            required=True,
            description="Set the scope for message recipients. "
            "The 'ALL' is valid only when a user has a specific permission.",
        )
        event_id = graphene.ID()
        occurrence_ids = graphene.List(graphene.NonNull(graphene.ID))
        send_directly = graphene.Boolean(
            default=False, description="Sends the message directly after the save"
        )

    message = graphene.Field(MessageNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user
        send_directly = kwargs.pop("send_directly", False)
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
            data["recipient_selection"],
            data["event"],
            occurrences,
            user,
            data["project"],
        )
        validate_event_and_occurrences(data["event"], occurrences)

        message = Message.objects.create_translatable_object(**data)
        if occurrences:
            message.occurrences.set(occurrences)

        logger.info(
            f"user {info.context.user.uuid} added message {message} with data {kwargs}"
        )

        if send_directly:
            message.send()
            logger.info(f"user {info.context.user.uuid} sent message {message}")

        return AddMessageMutation(message=message)


class UpdateMessageMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()
        protocol = ProtocolType(default=Message.EMAIL)
        translations = graphene.List(MessageTranslationsInput)
        project_id = graphene.ID()
        recipient_selection = RecipientSelectionEnum(
            description="Set the scope for message recipients. "
            "The 'ALL' is valid only when a user has a specific permission.",
        )
        event_id = graphene.ID()
        occurrence_ids = graphene.List(graphene.NonNull(graphene.ID))

    message = graphene.Field(MessageNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user
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
                data.get("event", message.event),
                occurrences,
                user,
                data.get("project_id", message.project),
            )
        validate_event_and_occurrences(
            data.get("event", message.event),
            occurrences if occurrences is not None else message.occurrences.all(),
        )

        update_object_with_translations(message, data)

        if occurrences is not None:
            message.occurrences.set(occurrences)

        logger.info(
            f"user {info.context.user.uuid} updated message {message} with data {kwargs}"  # noqa: E501
        )

        return UpdateMessageMutation(message=message)


def validate_recipient_selection_and_data(
    recipient_selection: RecipientSelectionEnum,
    event: Optional[Event],
    occurrences: Optional[List[Occurrence]],
    user: Optional[User],
    project: Optional[Project],
):
    if (
        recipient_selection == RecipientSelectionEnum.ALL.value
        and not user.can_send_messages_to_all_in_project(project)
    ):
        raise PermissionDenied(
            "User cannot send to ALL recipients "
            "without having a permission 'message.can_send_to_all_in_project' for that"
        )

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
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        message = get_obj_if_user_can_administer(info, kwargs["id"], Message)
        user = info.context.user

        try:
            validate_recipient_selection_and_data(
                message.recipient_selection,
                message.event,
                message.occurrences,
                user,
                message.project,
            )
            message.send()
        except AlreadySentError:
            raise MessageAlreadySentError(
                "Cannot send because the message has already been sent."
            )
        except PermissionDenied as e:
            raise e

        logger.info(f"user {info.context.user.uuid} sent message {message}")

        return SendMessageMutation(message=message)


class DeleteMessageMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    @classmethod
    @project_user_required
    @map_enums_to_values_in_kwargs
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
    messages = DjangoFilterAndOffsetConnectionField(MessageNode)


class Mutation:
    add_message = AddMessageMutation.Field()
    update_message = UpdateMessageMutation.Field()
    send_message = SendMessageMutation.Field()
    delete_message = DeleteMessageMutation.Field()

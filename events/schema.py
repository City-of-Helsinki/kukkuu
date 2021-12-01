import logging
from copy import deepcopy

import graphene
from django.apps import apps
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Count, Prefetch
from django.utils import timezone
from django.utils.translation import get_language
from graphene import Connection, ObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql_relay import from_global_id

from children.models import Child
from children.schema import ChildNode
from common.schema import LanguageEnum
from common.utils import (
    get_node_id_from_global_id,
    get_obj_if_user_can_administer,
    login_required,
    project_user_required,
    update_object,
    update_object_with_translations,
)
from events.filters import EventFilter, OccurrenceFilter
from events.models import Enrolment, Event, EventGroup, NoFreePasswordsError, Occurrence
from kukkuu.exceptions import (
    ChildAlreadyJoinedEventError,
    DataValidationError,
    EventAlreadyPublishedError,
    EventGroupAlreadyPublishedError,
    IneligibleOccurrenceEnrolment,
    NoFreeTicketSystemPasswordsError,
    ObjectDoesNotExistError,
    OccurrenceIsFullError,
    PastEnrolmentError,
    PastOccurrenceError,
    SingleEventsDisallowedError,
)
from kukkuu.utils import get_kukkuu_error_by_code
from projects.models import Project
from venues.models import Venue

logger = logging.getLogger(__name__)

EventTranslation = apps.get_model("events", "EventTranslation")

EventGroupTranslation = apps.get_model("events", "EventGroupTranslation")


def validate_enrolment(child, occurrence):
    if child.project != occurrence.event.project:
        raise IneligibleOccurrenceEnrolment(
            "Child does not belong to the project event"
        )
    if child.occurrences.filter(event=occurrence.event).exists():
        raise ChildAlreadyJoinedEventError("Child already joined this event")
    if occurrence.event.event_group and child.occurrences.filter(
        event__event_group=occurrence.event.event_group
    ):
        raise ChildAlreadyJoinedEventError(
            "Child already joined an event of this event group"
        )
    if occurrence.enrolments.count() >= occurrence.get_capacity():
        raise OccurrenceIsFullError("Maximum enrolments created")
    if occurrence.time < timezone.now():
        raise PastOccurrenceError("Cannot join occurrence in the past")


def validate_enrolment_deletion(enrolment):
    if not enrolment.is_upcoming():
        raise PastEnrolmentError(
            "Cannot unenrol from an occurrence that is in the past."
        )


class EventParticipantsPerInvite(graphene.Enum):
    CHILD_AND_GUARDIAN = "child_and_guardian"
    CHILD_AND_1_OR_2_GUARDIANS = "child_and_1_or_2_guardians"
    FAMILY = "family"


class TicketSystem(graphene.Enum):
    INTERNAL = "internal"
    TICKETMASTER = "ticketmaster"


class EventTicketSystem(graphene.Interface):
    # workaround needed because we have field named "type"
    type_ = TicketSystem(required=True, name="type")

    def resolve_type_(self, info, **kwargs):
        return self.ticket_system

    @classmethod
    def resolve_type(cls, instance, info):
        if instance.ticket_system == Event.INTERNAL:
            return InternalEventTicketSystem
        elif instance.ticket_system == Event.TICKETMASTER:
            return TicketmasterEventTicketSystem
        else:
            raise Exception(f'Invalid ticket system "{instance.ticket_system}".')


class TicketmasterEventTicketSystem(ObjectType):
    child_password = graphene.String(child_id=graphene.ID(required=True), required=True)

    class Meta:
        interfaces = (EventTicketSystem,)

    def resolve_child_password(self, info, **kwargs):
        try:
            child = Child.objects.user_can_view(info.context.user).get(
                id=get_node_id_from_global_id(kwargs["child_id"], "ChildNode")
            )
        except Child.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

        try:
            return self.get_or_assign_ticket_system_password(child)
        except NoFreePasswordsError as e:
            raise NoFreeTicketSystemPasswordsError(e)


class InternalEventTicketSystem(ObjectType):
    class Meta:
        interfaces = (EventTicketSystem,)


class EventTranslationType(DjangoObjectType):
    language_code = LanguageEnum(required=True)

    class Meta:
        model = EventTranslation
        exclude = ("id", "master")


class EventNode(DjangoObjectType):
    name = graphene.String()
    description = graphene.String()
    short_description = graphene.String()
    image_alt_text = graphene.String()
    participants_per_invite = EventParticipantsPerInvite(required=True)
    ticket_system = graphene.Field(EventTicketSystem)

    class Meta:
        model = Event
        interfaces = (relay.Node,)
        filterset_class = EventFilter
        fields = (
            "id",
            "created_at",
            "updated_at",
            "image",
            "image_alt_text",
            "participants_per_invite",
            "duration",
            "capacity_per_occurrence",
            "published_at",
            "project",
            "event_group",
            "ready_for_event_group_publishing",
            "translations",
            "occurrences",
            "messages",
            "name",
            "description",
            "short_description",
            "ticket_system",
        )

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        lang = get_language()
        return (
            queryset.user_can_view(info.context.user)
            .prefetch_related(
                Prefetch(
                    "translations",
                    queryset=EventTranslation.objects.order_by("language_code"),
                )
            )
            .order_by("-created_at")
            .language(lang)
        )

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return super().get_node(info, id)

    def resolve_image(self, info, **kwargs):
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return ""

    def resolve_occurrences(self, info, **kwargs):
        return self.occurrences.annotate(
            enrolment_count=Count("enrolments", distinct=True)
        ).order_by("time")

    def resolve_translations(self, info, **kwargs):
        return self.translations.order_by("language_code")

    def resolve_ticket_system(self, info, **kwargs):
        # Event object is needed for resolving EventTicketSystem fields
        return self


class EventConnection(Connection):
    class Meta:
        node = EventNode


class EventGroupTranslationType(DjangoObjectType):
    language_code = LanguageEnum(required=True)

    class Meta:
        model = EventGroupTranslation
        exclude = ("id", "master")


class EventGroupNode(DjangoObjectType):
    name = graphene.String()
    description = graphene.String()
    short_description = graphene.String()
    image_alt_text = graphene.String()

    class Meta:
        model = EventGroup
        interfaces = (relay.Node,)
        fields = (
            "id",
            "created_at",
            "updated_at",
            "name",
            "description",
            "short_description",
            "image",
            "image_alt_text",
            "published_at",
            "project",
            "translations",
            "events",
        )
        filter_fields = ("project_id",)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        lang = get_language()
        return (
            queryset.user_can_view(info.context.user)
            .prefetch_related(
                Prefetch(
                    "translations",
                    queryset=EventGroupTranslation.objects.order_by("language_code"),
                )
            )
            .order_by("-created_at")
            .language(lang)
        )

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return super().get_node(info, id)

    def resolve_translations(self, info, **kwargs):
        return self.translations.order_by("language_code")


class EventOrEventGroup(graphene.Union):
    class Meta:
        types = (EventNode, EventGroupNode)


class EventOrEventGroupConnection(Connection):
    class Meta:
        node = EventOrEventGroup


class EventGroupConnection(Connection):
    class Meta:
        node = EventGroupNode


class OccurrenceTicketSystem(graphene.Interface):
    # workaround needed because we have field named "type"
    type_ = TicketSystem(required=True, name="type")

    def resolve_type_(self, info, **kwargs):
        return self.event.ticket_system

    @classmethod
    def resolve_type(cls, instance, info):
        ticket_system = instance.event.ticket_system

        if ticket_system == Event.INTERNAL:
            return InternalOccurrenceTicketSystem
        elif ticket_system == Event.TICKETMASTER:
            return TicketmasterOccurrenceTicketSystem
        else:
            raise Exception(f'Invalid ticket system "{ticket_system}".')


class TicketmasterOccurrenceTicketSystem(ObjectType):
    url = graphene.String(required=True)

    class Meta:
        interfaces = (OccurrenceTicketSystem,)

    def resolve_url(self, info, **kwargs):
        return self.ticket_system_url


class InternalOccurrenceTicketSystem(ObjectType):
    class Meta:
        interfaces = (OccurrenceTicketSystem,)


class OccurrenceNode(DjangoObjectType):
    remaining_capacity = graphene.Int()
    occurrence_language = LanguageEnum(required=True)
    enrolment_count = graphene.Int(required=True)
    capacity = graphene.Int()
    child_has_free_spot_notification_subscription = graphene.Boolean(
        child_id=graphene.ID()
    )
    ticket_system = graphene.Field(OccurrenceTicketSystem)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return (
            queryset.user_can_view(info.context.user)
            .annotate(enrolment_count=Count("enrolments", distinct=True))
            .order_by("time")
        )

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return super().get_node(info, id)

    def resolve_remaining_capacity(self, info, **kwargs):
        return self.get_remaining_capacity()

    def resolve_enrolment_count(self, info, **kwargs):
        return self.get_enrolment_count()

    def resolve_capacity(self, info, **kwargs):
        return self.get_capacity()

    def resolve_child_has_free_spot_notification_subscription(self, info, **kwargs):
        child_id = get_node_id_from_global_id(kwargs["child_id"], "ChildNode")
        if not child_id:
            return None

        try:
            return (
                Child.objects.user_can_view(info.context.user)
                .get(pk=child_id)
                .free_spot_notification_subscriptions.filter(occurrence_id=self.id)
                .exists()
            )
        except Child.DoesNotExist:
            return None

    def resolve_ticket_system(self, info, **kwargs):
        # Occurrence object is needed for resolving OccurrenceTicketSystem fields
        return self

    class Meta:
        model = Occurrence
        interfaces = (relay.Node,)
        filterset_class = OccurrenceFilter
        fields = (
            "id",
            "created_at",
            "updated_at",
            "time",
            "event",
            "venue",
            "children",
            "occurrence_language",
            "enrolments",
            "capacity",
            "capacity_override",
            "remaining_capacity",
            "enrolment_count",
            "free_spot_notification_subscriptions",
            "child_has_free_spot_notification_subscription",
            "ticket_system",
        )


class EnrolmentNode(DjangoObjectType):
    class Meta:
        model = Enrolment
        interfaces = (relay.Node,)
        fields = ("occurrence", "child", "attended", "created_at", "updated_at")

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return queryset.user_can_view(info.context.user)


class EventTranslationsInput(graphene.InputObjectType):
    name = graphene.String()
    short_description = graphene.String()
    description = graphene.String()
    image_alt_text = graphene.String()
    language_code = LanguageEnum(required=True)


class EventTicketSystemInput(graphene.InputObjectType):
    type = TicketSystem(
        required=True, description="Can be changed only if the event is unpublished."
    )


class AddEventMutation(graphene.relay.ClientIDMutation):
    class Input:
        translations = graphene.List(EventTranslationsInput)
        duration = graphene.Int()
        participants_per_invite = EventParticipantsPerInvite(required=True)
        capacity_per_occurrence = graphene.Int(
            description="Required for internal ticket system events."
        )
        image = Upload()
        project_id = graphene.GlobalID()
        event_group_id = graphene.GlobalID(required=False)
        ready_for_event_group_publishing = graphene.Boolean()
        ticket_system = EventTicketSystemInput()

    event = graphene.Field(EventNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        original_kwargs = deepcopy(kwargs)

        project = get_obj_if_user_can_administer(
            info, kwargs.pop("project_id"), Project
        )
        kwargs["project_id"] = project.pk
        if "event_group_id" in kwargs and kwargs["event_group_id"]:
            kwargs["event_group_id"] = get_obj_if_user_can_administer(
                info, kwargs.get("event_group_id"), EventGroup
            ).pk
        elif not project.single_events_allowed:
            raise SingleEventsDisallowedError(
                f"Single events are disallowed in project {project}."
            )

        ticket_system_type = kwargs.pop("ticket_system", {}).get("type")
        if ticket_system_type:
            kwargs["ticket_system"] = ticket_system_type

        event = Event.objects.create_translatable_object(**kwargs)

        try:
            event.clean()
        except ValidationError as e:
            raise DataValidationError(str(e))

        logger.info(
            f"user {info.context.user.uuid} added event {event} "
            f"with data {original_kwargs}"
        )

        return AddEventMutation(event=event)


class UpdateEventMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()
        duration = graphene.Int()
        participants_per_invite = EventParticipantsPerInvite()
        capacity_per_occurrence = graphene.Int()
        image = Upload()
        translations = graphene.List(EventTranslationsInput)
        project_id = graphene.GlobalID(required=False)
        event_group_id = graphene.GlobalID(required=False)
        ready_for_event_group_publishing = graphene.Boolean()
        ticket_system = EventTicketSystemInput()

    event = graphene.Field(EventNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        original_kwargs = deepcopy(kwargs)

        project_global_id = kwargs.pop("project_id", None)
        if project_global_id:
            kwargs["project_id"] = get_obj_if_user_can_administer(
                info, project_global_id, Project
            ).pk

        if "event_group_id" in kwargs and kwargs["event_group_id"]:
            kwargs["event_group_id"] = get_obj_if_user_can_administer(
                info, kwargs["event_group_id"], EventGroup
            ).pk

        event = get_obj_if_user_can_administer(info, kwargs.pop("id"), Event)

        ticket_system_type = kwargs.pop("ticket_system", {}).get("type")
        if ticket_system_type:
            if event.published_at and ticket_system_type != event.ticket_system:
                raise DataValidationError(
                    "Cannot change ticket system because the event is published."
                )
            kwargs["ticket_system"] = ticket_system_type

        update_object_with_translations(event, kwargs)

        try:
            event.clean()
        except ValidationError as e:
            raise DataValidationError(str(e))

        logger.info(
            f"user {info.context.user.uuid} updated event {event} "
            f"with data {original_kwargs}"
        )

        return UpdateEventMutation(event=event)


class DeleteEventMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        event = get_obj_if_user_can_administer(info, kwargs["id"], Event)
        event.delete()

        logger.info(f"user {info.context.user.uuid} deleted event {event}")

        return DeleteEventMutation()


class EnrolOccurrenceMutation(graphene.relay.ClientIDMutation):
    class Input:
        occurrence_id = graphene.GlobalID(description="Occurrence id of event")
        child_id = graphene.GlobalID(description="Guardian's child id")

    enrolment = graphene.Field(EnrolmentNode)

    @classmethod
    @login_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        occurrence_id = from_global_id(kwargs["occurrence_id"])[1]
        child_id = from_global_id(kwargs["child_id"])[1]
        user = info.context.user
        try:
            occurrence = Occurrence.objects.get(pk=occurrence_id)
        except Occurrence.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)
        try:
            child = Child.objects.user_can_update(user).get(pk=child_id)
        except Child.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)
        validate_enrolment(child, occurrence)
        enrolment = Enrolment.objects.create(child=child, occurrence=occurrence)

        logger.info(
            f"user {user.uuid} enrolled child {child.pk} to occurrence {occurrence}"
        )

        return EnrolOccurrenceMutation(enrolment=enrolment)


class UnenrolOccurrenceMutation(graphene.relay.ClientIDMutation):
    class Input:
        occurrence_id = graphene.GlobalID(description="Occurrence id of event")
        child_id = graphene.GlobalID(description="Guardian's child id")

    occurrence = graphene.Field(OccurrenceNode)
    child = graphene.Field(ChildNode)

    @classmethod
    @login_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        occurrence_id = from_global_id(kwargs["occurrence_id"])[1]
        child_id = from_global_id(kwargs["child_id"])[1]
        user = info.context.user
        try:
            child = Child.objects.user_can_update(user).get(pk=child_id)
        except Child.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

        try:
            enrolment = child.enrolments.select_related("occurrence").get(
                occurrence_id=occurrence_id
            )
        except Enrolment.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

        validate_enrolment_deletion(enrolment)

        occurrence = enrolment.occurrence
        enrolment.delete_and_send_notification()

        logger.info(
            f"user {user.uuid} unenrolled child {child.pk} from occurrence {occurrence}"
        )

        return UnenrolOccurrenceMutation(child=child, occurrence=occurrence)


class SetEnrolmentAttendanceMutation(graphene.relay.ClientIDMutation):
    class Input:
        enrolment_id = graphene.GlobalID()
        attended = graphene.Boolean(
            description="This field is required (but it can be null)."
        )

    enrolment = graphene.Field(EnrolmentNode)

    @classmethod
    @login_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        if "attended" not in kwargs:
            raise DataValidationError('"attended" is required.')

        enrolment = get_obj_if_user_can_administer(
            info, kwargs["enrolment_id"], Enrolment
        )

        enrolment.attended = kwargs["attended"]
        enrolment.save()

        logger.info(
            f"user {info.context.user.uuid} set enrolment {enrolment} attendance to "
            f"{kwargs['attended']}"
        )

        return SetEnrolmentAttendanceMutation(enrolment=enrolment)


class OccurrenceTicketSystemInput(graphene.InputObjectType):
    url = graphene.String()


class AddOccurrenceMutation(graphene.relay.ClientIDMutation):
    class Input:
        time = graphene.DateTime(required=True)
        event_id = graphene.GlobalID()
        venue_id = graphene.GlobalID()
        occurrence_language = LanguageEnum()
        capacity_override = graphene.Int()
        ticket_system = OccurrenceTicketSystemInput()

    occurrence = graphene.Field(OccurrenceNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        original_kwargs = deepcopy(kwargs)

        kwargs["event_id"] = get_obj_if_user_can_administer(
            info, kwargs["event_id"], Event
        ).pk
        kwargs["venue_id"] = get_obj_if_user_can_administer(
            info, kwargs["venue_id"], Venue
        ).pk

        ticket_system_url = kwargs.pop("ticket_system", {}).get("url")
        if ticket_system_url is not None:
            kwargs["ticket_system_url"] = ticket_system_url

        occurrence = Occurrence.objects.create(**kwargs)

        # needed because enrolment_count is an annotated field
        occurrence.enrolment_count = 0

        logger.info(
            f"user {info.context.user.uuid} added occurrence {occurrence} with data "
            f"{original_kwargs}"
        )

        return AddOccurrenceMutation(occurrence=occurrence)


class UpdateOccurrenceMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()
        time = graphene.DateTime()
        event_id = graphene.GlobalID(required=False)
        venue_id = graphene.GlobalID(required=False)
        occurrence_language = LanguageEnum()
        capacity_override = graphene.Int()
        ticket_system = OccurrenceTicketSystemInput()

    occurrence = graphene.Field(OccurrenceNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        original_kwargs = deepcopy(kwargs)
        occurrence = get_obj_if_user_can_administer(info, kwargs.pop("id"), Occurrence)

        if kwargs.get("event_id"):
            kwargs["event_id"] = get_obj_if_user_can_administer(
                info, kwargs["event_id"], Event
            ).pk

        if kwargs.get("venue_id"):
            kwargs["venue_id"] = get_obj_if_user_can_administer(
                info, kwargs["venue_id"], Venue
            ).pk

        ticket_system_url = kwargs.pop("ticket_system", {}).get("url")
        if ticket_system_url is not None:
            kwargs["ticket_system_url"] = ticket_system_url

        update_object(occurrence, kwargs)

        try:
            occurrence.clean()
        except ValidationError as e:
            kukkuu_error = get_kukkuu_error_by_code(e.code)
            if kukkuu_error:
                raise kukkuu_error(e.message)
            else:
                raise

        logger.info(
            f"user {info.context.user.uuid} updated occurrence {occurrence} "
            f"of event {occurrence.event} with data {original_kwargs}"
        )

        return UpdateOccurrenceMutation(occurrence=occurrence)


class DeleteOccurrenceMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        occurrence = get_obj_if_user_can_administer(info, kwargs["id"], Occurrence)
        log_text = (
            f"user {info.context.user.uuid} deleted occurrence {occurrence} "
            f"of event {occurrence.event}"
        )
        occurrence.delete()

        logger.info(log_text)

        return DeleteOccurrenceMutation()


class PublishEventMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    event = graphene.Field(EventNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        event = get_obj_if_user_can_administer(info, kwargs["id"], Event)
        user = info.context.user

        if not event.can_user_publish(user):
            raise PermissionDenied("No permission to publish the event.")

        if event.is_published():
            raise EventAlreadyPublishedError("Event is already published")

        try:
            event.publish()
        except ValidationError as e:
            kukkuu_error = get_kukkuu_error_by_code(e.code)
            if kukkuu_error:
                raise kukkuu_error(e.message)
            else:
                raise

        logger.info(f"user {user.uuid} published event {event}")

        return PublishEventMutation(event=event)


class EventGroupTranslationsInput(graphene.InputObjectType):
    name = graphene.String()
    short_description = graphene.String()
    description = graphene.String()
    image_alt_text = graphene.String()
    language_code = LanguageEnum(required=True)


class AddEventGroupMutation(graphene.relay.ClientIDMutation):
    class Input:
        translations = graphene.List(EventGroupTranslationsInput)
        image = Upload()
        project_id = graphene.GlobalID()

    event_group = graphene.Field(EventGroupNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user

        project = get_obj_if_user_can_administer(
            info, kwargs.pop("project_id"), Project
        )
        if not user.can_manage_event_groups_in_project(project):
            raise PermissionDenied()

        kwargs["project_id"] = project.pk
        event_group = EventGroup.objects.create_translatable_object(**kwargs)

        logger.info(
            f"user {user.uuid} added event group {event_group} " f"with data {kwargs}"
        )

        return AddEventGroupMutation(event_group=event_group)


class UpdateEventGroupMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()
        image = Upload()
        translations = graphene.List(EventGroupTranslationsInput)
        project_id = graphene.GlobalID(required=False)

    event_group = graphene.Field(EventGroupNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        event_group = get_obj_if_user_can_administer(info, kwargs.pop("id"), EventGroup)
        user = info.context.user
        project = event_group.project

        project_global_id = kwargs.pop("project_id", None)
        if project_global_id:
            project = get_obj_if_user_can_administer(info, project_global_id, Project)
            kwargs["project_id"] = project.pk

        if not user.can_manage_event_groups_in_project(project):
            raise PermissionDenied()

        update_object_with_translations(event_group, kwargs)

        logger.info(
            f"user {user.uuid} updated event group {event_group} " f"with data {kwargs}"
        )

        return UpdateEventGroupMutation(event_group=event_group)


class DeleteEventGroupMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    @classmethod
    @project_user_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        event_group = get_obj_if_user_can_administer(info, kwargs["id"], EventGroup)
        user = info.context.user

        if not user.can_manage_event_groups_in_project(event_group.project):
            raise PermissionDenied()

        event_group.delete()

        logger.info(f"user {user.uuid} deleted event group {event_group}")

        return DeleteEventGroupMutation()


class PublishEventGroupMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    event_group = graphene.Field(EventGroupNode)

    @classmethod
    @project_user_required
    def mutate_and_get_payload(cls, root, info, **kwargs):
        event_group = get_obj_if_user_can_administer(info, kwargs["id"], EventGroup)
        user = info.context.user

        if not event_group.can_user_publish(user):
            raise PermissionDenied("No permission to publish the event group.")

        if event_group.is_published():
            raise EventGroupAlreadyPublishedError("Event group is already published")

        try:
            event_group.publish()
        except ValidationError as e:
            kukkuu_error = get_kukkuu_error_by_code(e.code)
            if kukkuu_error:
                raise kukkuu_error(e.message)
            else:
                raise

        logger.info(f"user {user.uuid} published event group {event_group}")

        return PublishEventGroupMutation(event_group=event_group)


class Query:
    events = DjangoFilterConnectionField(EventNode)
    events_and_event_groups = graphene.ConnectionField(
        EventOrEventGroupConnection, project_id=graphene.ID()
    )
    occurrences = DjangoFilterConnectionField(OccurrenceNode)

    event = relay.Node.Field(EventNode)
    event_group = relay.Node.Field(EventGroupNode)
    occurrence = relay.Node.Field(OccurrenceNode)

    def resolve_events_and_event_groups(self, info, **kwargs):
        event_qs = Event.objects.filter(event_group=None)
        event_group_qs = EventGroup.objects.all()

        if "project_id" in kwargs:
            project_id = get_node_id_from_global_id(kwargs["project_id"], "ProjectNode")
            event_qs = event_qs.filter(project_id=project_id)
            event_group_qs = event_group_qs.filter(project_id=project_id)

        return sorted(
            (
                *EventNode.get_queryset(event_qs, info),
                *EventGroupNode.get_queryset(event_group_qs, info),
            ),
            key=lambda e: e.created_at,
            reverse=True,
        )


class Mutation:
    add_event = AddEventMutation.Field()
    update_event = UpdateEventMutation.Field()
    delete_event = DeleteEventMutation.Field()
    publish_event = PublishEventMutation.Field()

    add_occurrence = AddOccurrenceMutation.Field()
    update_occurrence = UpdateOccurrenceMutation.Field()
    delete_occurrence = DeleteOccurrenceMutation.Field()
    enrol_occurrence = EnrolOccurrenceMutation.Field()
    unenrol_occurrence = UnenrolOccurrenceMutation.Field()
    set_enrolment_attendance = SetEnrolmentAttendanceMutation.Field()

    add_event_group = AddEventGroupMutation.Field()
    update_event_group = UpdateEventGroupMutation.Field()
    delete_event_group = DeleteEventGroupMutation.Field()
    publish_event_group = PublishEventGroupMutation.Field()

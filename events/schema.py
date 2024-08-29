import logging
from copy import deepcopy
from typing import List, Optional

import graphene
from django.apps import apps
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.utils import timezone
from django.utils.translation import get_language
from graphene import Connection, ObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql_relay import from_global_id

from children.models import Child
from children.schema import ChildNode
from common.schema import ErrorType, LanguageEnum
from common.utils import (
    check_can_user_administer,
    get_node_id_from_global_id,
    get_obj_if_user_can_administer,
    login_required,
    map_enums_to_values_in_kwargs,
    project_user_required,
    update_object,
    update_object_with_translations,
)
from events.exceptions import NoFreePasswordsError, PasswordAlreadyAssignedError
from events.filters import EventFilter, OccurrenceFilter
from events.models import Enrolment, Event, EventGroup, Occurrence, TicketSystemPassword
from events.ticket_service import check_ticket_validity
from kukkuu.exceptions import (
    ChildAlreadyJoinedEventError,
    DataValidationError,
    EventAlreadyPublishedError,
    EventGroupAlreadyPublishedError,
    EventNotPublishedError,
    IneligibleOccurrenceEnrolment,
    NoFreeTicketSystemPasswordsError,
    ObjectDoesNotExistError,
    OccurrenceIsFullError,
    OccurrenceYearMismatchError,
    PastEnrolmentError,
    PastOccurrenceError,
    SingleEventsDisallowedError,
    TicketSystemPasswordAlreadyAssignedError,
    TicketSystemPasswordNothingToImportError,
)
from kukkuu.utils import get_kukkuu_error_by_code
from projects.models import Project
from venues.models import Venue

logger = logging.getLogger(__name__)

EventTranslation = apps.get_model("events", "EventTranslation")

EventGroupTranslation = apps.get_model("events", "EventGroupTranslation")


def validate_enrolment(child, occurrence):
    if not occurrence.event.is_published():
        raise EventNotPublishedError("Event is not published")

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

    if (
        child.get_enrolment_count(year=occurrence.time.year)
        >= occurrence.event.project.enrolment_limit
    ):
        raise IneligibleOccurrenceEnrolment("Yearly enrolment limit has been reached")


def validate_enrolment_deletion(enrolment):
    if not enrolment.is_upcoming():
        raise PastEnrolmentError(
            "Cannot unenrol from an occurrence that is in the past."
        )


def validate_occurrence_input(kwargs, occurrence: Occurrence = None):
    if time := kwargs.get("time"):
        if occurrence:
            # Don't consider the occurrence which is being updated
            existing_occurrences = occurrence.event.occurrences.exclude(
                pk=occurrence.pk
            )
        else:
            event = Event.objects.get(pk=kwargs["event_id"])
            existing_occurrences = event.occurrences.all()

        if (
            existing_occurrences.exists()
            and not existing_occurrences.filter(time__year=time.year).exists()
        ):
            raise OccurrenceYearMismatchError(
                "Occurrence has different year than the rest of the event occurrences"
            )


class EventParticipantsPerInvite(graphene.Enum):
    CHILD_AND_GUARDIAN = "child_and_guardian"
    CHILD_AND_1_OR_2_GUARDIANS = "child_and_1_or_2_guardians"
    FAMILY = "family"


class TicketSystem(graphene.Enum):
    INTERNAL = "internal"
    TICKETMASTER = "ticketmaster"
    LIPPUPISTE = "lippupiste"


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
        elif instance.ticket_system == Event.LIPPUPISTE:
            return LippupisteEventTicketSystem
        else:
            raise Exception(f'Invalid ticket system "{instance.ticket_system}".')


class ExternalEventTicketSystem(ObjectType):
    child_password = graphene.String(child_id=graphene.ID())
    free_password_count = graphene.Int(required=True)
    used_password_count = graphene.Int(required=True)
    url = graphene.String(required=True)
    end_time = graphene.DateTime()

    class Meta:
        abstract = True

    def resolve_child_password(event: Event, info, **kwargs):
        try:
            child = Child.objects.user_can_view(info.context.user).get(
                id=get_node_id_from_global_id(kwargs["child_id"], "ChildNode")
            )
            return event.ticket_system_passwords.get(child=child).value
        except TicketSystemPassword.DoesNotExist:
            return None
        except Child.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

    def resolve_free_password_count(self, info, **kwargs):
        if not self.can_user_administer(info.context.user):
            raise PermissionDenied()
        return self.ticket_system_passwords.free().count()

    def resolve_used_password_count(self, info, **kwargs):
        if not self.can_user_administer(info.context.user):
            raise PermissionDenied()
        return self.ticket_system_passwords.used().count()

    def resolve_url(event: Event, info, **kwargs):
        return event.ticket_system_url

    def resolve_end_time(event: Event, info, **kwargs):
        return event.ticket_system_end_time


class TicketmasterEventTicketSystem(ExternalEventTicketSystem):
    class Meta:
        interfaces = (EventTicketSystem,)


class LippupisteEventTicketSystem(ExternalEventTicketSystem):
    class Meta:
        interfaces = (EventTicketSystem,)


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
    can_child_enroll = graphene.Boolean(child_id=graphene.ID(required=True))

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

    def resolve_can_child_enroll(self: Event, info, **kwargs) -> Optional[bool]:
        child_id = get_node_id_from_global_id(kwargs["child_id"], "ChildNode")
        try:
            child = Child.objects.user_can_view(info.context.user).get(id=child_id)
        except Child.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)
        return self.can_child_enroll(child)


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
    can_child_enroll = graphene.Boolean(child_id=graphene.ID(required=True))

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

    def resolve_translations(self: EventGroup, info, **kwargs):
        return self.translations.order_by("language_code")

    def resolve_can_child_enroll(self: EventGroup, info, **kwargs) -> Optional[bool]:
        child_id = get_node_id_from_global_id(kwargs["child_id"], "ChildNode")
        try:
            child = Child.objects.user_can_view(info.context.user).get(id=child_id)
        except Child.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)
        return self.can_child_enroll(child)


class EventOrEventGroupUnion(graphene.Union):
    class Meta:
        types = (EventNode, EventGroupNode)


class EventOrEventGroupConnection(Connection):
    class Meta:
        node = EventOrEventGroupUnion


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
        elif ticket_system == Event.LIPPUPISTE:
            return LippupisteOccurrenceTicketSystem
        else:
            raise Exception(f'Invalid ticket system "{ticket_system}".')


class ExternalOccurrenceTicketSystem(ObjectType):
    url = graphene.String(required=True)

    def resolve_url(self, info, **kwargs):
        return self.ticket_system_url


class TicketmasterOccurrenceTicketSystem(ExternalOccurrenceTicketSystem):
    class Meta:
        interfaces = (OccurrenceTicketSystem,)


class LippupisteOccurrenceTicketSystem(ExternalOccurrenceTicketSystem):
    class Meta:
        interfaces = (OccurrenceTicketSystem,)


class InternalOccurrenceTicketSystem(ObjectType):
    class Meta:
        interfaces = (OccurrenceTicketSystem,)


class OccurrenceNode(DjangoObjectType):
    remaining_capacity = graphene.Int()
    occurrence_language = LanguageEnum(required=True)
    enrolment_count = graphene.Int(required=True)
    attended_enrolment_count = graphene.Int(required=True)
    free_spot_notification_subscription_count = graphene.Int(required=True)
    capacity = graphene.Int()
    child_has_free_spot_notification_subscription = graphene.Boolean(
        child_id=graphene.ID()
    )
    ticket_system = graphene.Field(
        OccurrenceTicketSystem,
        deprecation_reason=(
            "There is no need for this because the only field ticketSystemUrl has been "
            "moved to EventNode.ticketSystem."
        ),
    )

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        VenueTranslation = apps.get_model("venues", "VenueTranslation")

        return (
            queryset.user_can_view(info.context.user)
            .with_end_time()
            .with_enrolment_count()
            .with_attended_enrolment_count()
            .with_free_spot_notification_subscription_count()
            .order_by("time")
            .select_related("event", "event__project", "venue", "venue__project")
            .prefetch_related(
                Prefetch(
                    "venue__translations",
                    queryset=VenueTranslation.objects.order_by("language_code"),
                    to_attr="prefetched_translations",
                )
            )
        )

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return super().get_node(info, id)

    def resolve_remaining_capacity(self, info, **kwargs):
        return self.get_remaining_capacity()

    def resolve_enrolment_count(self, info, **kwargs):
        return self.get_enrolment_count()

    def resolve_attended_enrolment_count(self, info, **kwargs):
        check_can_user_administer(self, info.context.user)
        return self.get_attended_enrolment_count()

    def resolve_free_spot_notification_subscription_count(self, info, **kwargs):
        check_can_user_administer(self, info.context.user)
        return self.get_free_spot_notification_subscription_count()

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
    reference_id = graphene.String(description="An unique encoded reference id")

    class Meta:
        model = Enrolment
        interfaces = (relay.Node,)
        fields = ("occurrence", "child", "attended", "created_at", "updated_at")

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return queryset.user_can_view(info.context.user)

    def resolve_reference_id(self, info, **kwargs):
        return self.reference_id


class ExternalTicketSystemEnrolmentNode(DjangoObjectType):
    created_at = graphene.DateTime(required=True)

    class Meta:
        abstract = True

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return queryset.filter(
            Q(child__guardians__user=info.context.user)
            | Q(child__project__in=info.context.user.administered_projects)
        ).distinct()

    def resolve_created_at(self, info):
        return self.assigned_at


class TicketmasterEnrolmentNode(ExternalTicketSystemEnrolmentNode):
    class Meta:
        model = TicketSystemPassword
        interfaces = (relay.Node,)
        fields = ("event", "created_at")

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        q = super().get_queryset(queryset, info)
        return q.filter(event__ticket_system=Event.TICKETMASTER)


class LippupisteEnrolmentNode(ExternalTicketSystemEnrolmentNode):
    class Meta:
        model = TicketSystemPassword
        interfaces = (relay.Node,)
        fields = ("event", "created_at")

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return (
            super()
            .get_queryset(queryset, info)
            .filter(event__ticket_system=Event.LIPPUPISTE)
        )


class InternalOrTicketSystemEnrolmentUnion(graphene.Union):
    class Meta:
        types = (EnrolmentNode, TicketmasterEnrolmentNode, LippupisteEnrolmentNode)


class InternalOrTicketSystemEnrolmentConnection(Connection):
    class Meta:
        node = InternalOrTicketSystemEnrolmentUnion


class TicketVerificationNode(ObjectType):
    event_name = graphene.String(required=True, description="The name of the event")
    occurrence_time = graphene.DateTime(
        required=True, description="The time of the event occurrence"
    )
    venue_name = graphene.String(description="The name of the venue")
    validity = graphene.Boolean(required=True)


class EventTranslationsInput(graphene.InputObjectType):
    name = graphene.String()
    short_description = graphene.String()
    description = graphene.String()
    image_alt_text = graphene.String()
    language_code = LanguageEnum(required=True)


class AddEventTicketSystemInput(graphene.InputObjectType):
    type = TicketSystem(required=True)
    # TODO make this required when Kukkuu admin is updated to support it
    url = graphene.String()
    end_time = graphene.String()


class UpdateEventTicketSystemInput(graphene.InputObjectType):
    url = graphene.String()
    end_time = graphene.String()


class ImportTicketSystemPasswordsMutation(graphene.relay.ClientIDMutation):
    class Input:
        event_id = graphene.GlobalID(required=True)
        passwords = graphene.List(graphene.NonNull(graphene.String), required=True)

    event = graphene.Field(EventNode)
    passwords = graphene.List(
        graphene.String, description="A list of imported passwords"
    )
    errors = graphene.List(
        ErrorType,
        description="A list of passwords which could not be imported",
    )

    @classmethod
    @project_user_required
    @transaction.atomic
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        event_id = get_node_id_from_global_id(kwargs.get("event_id"), "EventNode")
        given_passwords = kwargs.get("passwords")

        if not given_passwords:
            raise TicketSystemPasswordNothingToImportError(
                "There is no passwords given to be imported. "
                "At least 1 password required."
            )

        try:
            event = Event.objects.user_can_view(info.context.user).get(pk=event_id)
        except Event.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

        # Save passwords one by one instead of bulk, to also collect the errors...
        (imported_passwords, errors) = cls._create_batch(
            event,
            [
                TicketSystemPassword(event=event, value=password)
                for password in given_passwords
            ],
        )

        return ImportTicketSystemPasswordsMutation(
            event=event,
            passwords=[
                ticket_system_password.value
                for ticket_system_password in imported_passwords
            ],
            errors=errors,
        )

    @classmethod
    def _create_batch(cls, event: Event, passwords_batch: List[TicketSystemPassword]):
        # Fetch the existing passwords for integrity test, because
        # if the passwords already exists,
        # an integrity error will be raised by bulk_create.
        existing_passwords = TicketSystemPassword.objects.filter(
            event=event, value__in=[p.value for p in passwords_batch]
        )
        # The errors can be collected before the bulk-create.
        # The Django's bulk_create does not return any errors or PKs
        # that could be used to check which instances were created and which were not.
        errors = (
            cls._get_errors_field_value(e.value for e in existing_passwords)
            if existing_passwords
            else None
        )

        passwords_to_be_imported = [
            p
            for p in passwords_batch
            if p.value not in [e.value for e in existing_passwords]
        ]

        imported_passwords = TicketSystemPassword.objects.bulk_create(
            passwords_to_be_imported
        )

        return imported_passwords, errors

    @classmethod
    def _get_errors_field_value(cls, passwords_with_errors: List[str]):
        return (
            [
                ErrorType(
                    field="passwords", message="Could not import password", value=p
                )
                for p in passwords_with_errors
            ]
            if passwords_with_errors
            else None
        )


class AssignTicketSystemPasswordMutation(graphene.relay.ClientIDMutation):
    class Input:
        event_id = graphene.GlobalID(required=True)
        child_id = graphene.GlobalID(required=True)

    event = graphene.Field(EventNode)
    child = graphene.Field(ChildNode)
    password = graphene.String(description="The assigned ticket system password")

    @classmethod
    @transaction.atomic
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        event_id = get_node_id_from_global_id(kwargs.get("event_id"), "EventNode")
        child_id = get_node_id_from_global_id(kwargs.get("child_id"), "ChildNode")

        try:
            event = Event.objects.user_can_view(info.context.user).get(pk=event_id)
            child = Child.objects.user_can_update(info.context.user).get(pk=child_id)
        except (Event.DoesNotExist, Child.DoesNotExist) as e:
            raise ObjectDoesNotExistError(e)

        try:
            password = TicketSystemPassword.objects.assign(event=event, child=child)
        except NoFreePasswordsError as e:
            raise NoFreeTicketSystemPasswordsError(str(e))
        except PasswordAlreadyAssignedError as e:
            raise TicketSystemPasswordAlreadyAssignedError(str(e))

        return AssignTicketSystemPasswordMutation(
            event=event, child=child, password=password.value
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
        ticket_system = AddEventTicketSystemInput()

    event = graphene.Field(EventNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    @map_enums_to_values_in_kwargs
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

        if ticket_system := kwargs.pop("ticket_system", None):
            kwargs.update(
                {
                    "ticket_system": ticket_system.get("type"),
                    "ticket_system_url": ticket_system.get(
                        "url",
                        # TODO this is a temporal value to keep Kukkuu admin UI working
                        # until it has the event URL implemented
                        "https://example.com",
                    ),
                    "ticket_system_end_time": ticket_system.get("end_time"),
                }
            )

        event = Event.objects.create_translatable_object(**kwargs)

        try:
            event.clean()
        except ValidationError as e:
            raise DataValidationError(str(e))

        logger.info(
            f"user {info.context.user.uuid} added event {event} "
            f"with data {original_kwargs}"
        )

        # The event object must contain objects as its properties where needed, and
        # this is probably the easiest way to achieve that. Without this for example
        # event.ticketSystemEndTime would be a string instead of a datetime object.
        event.refresh_from_db()

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
        ticket_system = UpdateEventTicketSystemInput()

    event = graphene.Field(EventNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        original_kwargs = deepcopy(kwargs)

        project_global_id = kwargs.pop("project_id", None)
        if project_global_id:
            kwargs["project_id"] = get_obj_if_user_can_administer(
                info, project_global_id, Project
            ).pk

        event_group_global_id = kwargs.pop("event_group_id", None)
        if event_group_global_id:
            kwargs["event_group_id"] = get_obj_if_user_can_administer(
                info, event_group_global_id, EventGroup
            ).pk

        event = get_obj_if_user_can_administer(info, kwargs.pop("id"), Event)

        if ticket_system := kwargs.pop("ticket_system", None):
            if "url" in ticket_system:
                kwargs["ticket_system_url"] = ticket_system.get("url", "")
            if "end_time" in ticket_system:
                kwargs["ticket_system_end_time"] = ticket_system.get("end_time")

        update_object_with_translations(event, kwargs)

        try:
            event.clean()
        except ValidationError as e:
            raise DataValidationError(str(e))

        logger.info(
            f"user {info.context.user.uuid} updated event {event} "
            f"with data {original_kwargs}"
        )

        # The event object must contain objects as its properties where needed, and
        # this is probably the easiest way to achieve that. Without this for example
        # event.ticketSystemEndTime would be a string instead of a datetime object.
        event.refresh_from_db()

        return UpdateEventMutation(event=event)


class DeleteEventMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    @classmethod
    @project_user_required
    @transaction.atomic
    @map_enums_to_values_in_kwargs
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
    @map_enums_to_values_in_kwargs
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
    @map_enums_to_values_in_kwargs
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
    @map_enums_to_values_in_kwargs
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
    @map_enums_to_values_in_kwargs
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

        validate_occurrence_input(kwargs)
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
    @map_enums_to_values_in_kwargs
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

        validate_occurrence_input(kwargs, occurrence=occurrence)
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
    @map_enums_to_values_in_kwargs
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
    @map_enums_to_values_in_kwargs
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
    @map_enums_to_values_in_kwargs
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
    @map_enums_to_values_in_kwargs
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
    @map_enums_to_values_in_kwargs
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
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        event_group = get_obj_if_user_can_administer(info, kwargs["id"], EventGroup)
        user = info.context.user

        if not event_group.can_user_publish(user):
            raise PermissionDenied("No permission to publish the event group.")

        if event_group.is_published() and not event_group.events.unpublished().exists():
            # Republishing an event group is allowed if new unpublished events exist
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
        EventOrEventGroupConnection,
        project_id=graphene.ID(),
        upcoming=graphene.Boolean(),
    )
    occurrences = DjangoFilterConnectionField(OccurrenceNode)

    event = relay.Node.Field(EventNode)
    event_group = relay.Node.Field(EventGroupNode)
    occurrence = relay.Node.Field(OccurrenceNode)
    verify_ticket = graphene.Field(
        TicketVerificationNode, reference_id=graphene.String(required=True)
    )

    def resolve_events_and_event_groups(self, info, **kwargs):
        event_qs = Event.objects.filter(event_group=None)
        event_group_qs = EventGroup.objects.all()

        if "project_id" in kwargs:
            project_id = get_node_id_from_global_id(kwargs["project_id"], "ProjectNode")
            event_qs = event_qs.filter(project_id=project_id)
            event_group_qs = event_group_qs.filter(project_id=project_id)

        if kwargs.get("upcoming", False):
            event_qs = event_qs.upcoming()
            event_group_qs = event_group_qs.upcoming()

        return sorted(
            (
                *EventNode.get_queryset(event_qs, info),
                *EventGroupNode.get_queryset(event_group_qs, info),
            ),
            key=lambda e: e.created_at,
            reverse=True,
        )

    def resolve_verify_ticket(self, info, **kwargs):
        enrolment_reference_id = kwargs.get("reference_id", None)
        enrolment, ticket_validity = check_ticket_validity(enrolment_reference_id)
        return TicketVerificationNode(
            event_name=enrolment.occurrence.event.name,
            occurrence_time=enrolment.occurrence.time,
            venue_name=enrolment.occurrence.venue.name,
            validity=ticket_validity,
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

    assign_ticket_system_password = AssignTicketSystemPasswordMutation.Field()
    import_ticket_system_passwords = ImportTicketSystemPasswordsMutation.Field()

import logging
from datetime import datetime, timedelta

import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone
from django.utils.timezone import localdate, make_aware
from django_ilmoitin.utils import send_notification
from graphene import relay
from graphene_django import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_relay import from_global_id

from children.notifications import NotificationType
from common.schema import set_obj_languages_spoken_at_home
from common.utils import login_required, update_object
from events.models import Event, Occurrence
from kukkuu.exceptions import (
    ApiUsageError,
    DataValidationError,
    MaxNumberOfChildrenPerGuardianError,
    ObjectDoesNotExistError,
)
from languages.schema import LanguageNode
from projects.models import Project
from users.models import Guardian
from users.schema import GuardianNode, LanguageEnum, validate_guardian_data

from .models import Child, postal_code_validator, Relationship

User = get_user_model()

logger = logging.getLogger(__name__)


class ChildrenConnection(graphene.Connection):
    class Meta:
        abstract = True

    count = graphene.Int(required=True)

    def resolve_count(self, info, **kwargs):
        return self.length


class ChildNode(DjangoObjectType):
    available_events = relay.ConnectionField(
        "events.schema.EventConnection",
        deprecation_reason=(
            "Doesn't exclude events when yearly limit of enrolments have been exceeded."
        ),
    )
    available_events_and_event_groups = relay.ConnectionField(
        "events.schema.EventOrEventGroupConnection",
        deprecation_reason=(
            "Doesn't exclude events when yearly limit of enrolments have been exceeded."
        ),
    )
    upcoming_events_and_event_groups = relay.ConnectionField(
        "events.schema.EventOrEventGroupConnection",
        description="All upcoming events and event groups for the child's project.",
    )
    past_events = relay.ConnectionField("events.schema.EventConnection")
    languages_spoken_at_home = DjangoConnectionField(LanguageNode)
    enrolment_count = graphene.Int(
        description="How many enrolments child has this year.", year=graphene.Int()
    )
    past_enrolment_count = graphene.Int(
        description="How many past enrolments child has this year.",
    )
    active_internal_and_ticket_system_enrolments = relay.ConnectionField(
        "events.schema.InternalOrTicketSystemEnrolmentConnection",
        description="All upcoming and ongoing (with leeway) internal and ticket system "
        "enrolments sorted by time.",
    )

    class Meta:
        model = Child
        interfaces = (relay.Node,)
        connection_class = ChildrenConnection
        fields = (
            "id",
            "created_at",
            "updated_at",
            "name",
            "postal_code",
            "birthyear",
            "guardians",
            "project",
            "languages_spoken_at_home",
            "relationships",
            "occurrences",
            "enrolments",
            "available_events",
            "past_events",
            "free_spot_notification_subscriptions",
        )
        filter_fields = ("project_id",)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return queryset.user_can_view(info.context.user).order_by("name", "created_at")

    @classmethod
    @login_required
    def get_node(cls, info, id):
        try:
            return cls._meta.model.objects.user_can_view(info.context.user).get(id=id)
        except cls._meta.model.DoesNotExist:
            return None

    def resolve_enrolment_count(self: Child, info, **kwargs):
        year = kwargs.get("year")
        return self.get_enrolment_count(year)

    def resolve_past_enrolment_count(self: Child, info, **kwargs):
        return self.get_enrolment_count(past=True)

    def resolve_past_events(self: Child, info, **kwargs):
        """
        Past events include:
          * internal ticket system Events the user has enrolled and the end time of the
            Enrolment's Occurrence is enough in the past. Enough means
            settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY amount of minutes.
          * external ticket system Events the user has a password to and the Event's
            ticket_system_end_time is in the past at all.
        """
        from events.schema import ExternalTicketSystemEnrolmentNode, OccurrenceNode

        published_events = self.project.events.user_can_view(
            info.context.user
        ).published()

        occurrences = self.occurrences.with_end_time()
        now = timezone.now()
        past_enough = now - timedelta(
            minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY
        )
        past_enough_enrolled_occurrences = occurrences.filter(
            end_time__lt=past_enough,
            event__in=published_events,
        ).select_related("event")

        past_ticket_system_passwords = (
            self.ticket_system_passwords.filter(
                (
                    ~Q(event__ticket_system=Event.INTERNAL)
                    & Q(event__ticket_system_end_time__lt=now)
                ),
                event__in=published_events,
            )
            .select_related("event")
            .annotate(end_time=F("event__ticket_system_end_time"))
        )

        occurrences_and_passwords = sorted(
            (
                *OccurrenceNode.get_queryset(past_enough_enrolled_occurrences, info),
                *ExternalTicketSystemEnrolmentNode.get_queryset(
                    past_ticket_system_passwords, info
                ),
            ),
            key=lambda x: x.end_time,
        )

        return [x.event for x in occurrences_and_passwords]

    def resolve_available_events(self: Child, info, **kwargs):
        return self.project.events.user_can_view(info.context.user).available(self)

    def resolve_upcoming_events_and_event_groups(self: Child, info, **kwargs):
        from events.schema import EventGroupNode, EventNode  # noqa

        upcoming_events = self.project.events.published().upcoming()
        upcoming_event_groups = self.project.event_groups.filter(
            events__in=upcoming_events
        )

        return sorted(
            (
                *EventNode.get_queryset(upcoming_events.filter(event_group=None), info),
                *EventGroupNode.get_queryset(upcoming_event_groups, info),
            ),
            key=lambda e: e.published_at,
            reverse=True,
        )

    def resolve_available_events_and_event_groups(self: Child, info, **kwargs):
        from events.schema import EventGroupNode, EventNode  # noqa

        available_events = self.project.events.available(self)
        available_event_groups = self.project.event_groups.filter(
            events__in=available_events
        )

        return sorted(
            (
                *EventNode.get_queryset(
                    available_events.filter(event_group=None), info
                ),
                *EventGroupNode.get_queryset(available_event_groups, info),
            ),
            key=lambda e: e.published_at,
            reverse=True,
        )

    def resolve_occurrences(self: Child, info, **kwargs):
        # Use distinct to avoid duplicated rows when querying nested occurrences
        return self.occurrences.distinct()

    def resolve_active_internal_and_ticket_system_enrolments(self, info, **kwargs):
        from events.schema import EnrolmentNode, ExternalTicketSystemEnrolmentNode

        active_occurrences = Occurrence.objects.upcoming_with_ongoing()
        internal_enrolments = self.enrolments.filter(
            occurrence__in=active_occurrences
        ).annotate(
            # Technically to be 100% correct we should use the occurrence's end time
            # instead of start time for sorting because for external ticket system
            # enrolments the event's end time is used,
            # but doing that would be way more complicated
            # and the difference not matter at all in practice.
            time=F("occurrence__time"),
            published_at=F("occurrence__event__published_at"),
        )
        ticket_system_passwords = (
            self.ticket_system_passwords.event_upcoming_or_ongoing().annotate(
                time=F("event__ticket_system_end_time"),
                published_at=F("event__published_at"),
            )
        )

        datetime_max = make_aware(datetime.max, timezone=timezone.utc)
        return sorted(
            (
                *EnrolmentNode.get_queryset(internal_enrolments, info),
                *ExternalTicketSystemEnrolmentNode.get_queryset(
                    ticket_system_passwords, info
                ),
            ),
            # Sort events by time with external ticket system events
            # without an end time as last,
            # and sort those by published at to keep the ordering stable.
            key=lambda e: (e.time or datetime_max, e.published_at),
        )


class RelationshipTypeEnum(graphene.Enum):
    PARENT = "parent"
    OTHER_GUARDIAN = "other_guardian"
    OTHER_RELATION = "other_relation"
    ADVOCATE = "advocate"


class RelationshipNode(DjangoObjectType):
    class Meta:
        model = Relationship
        interfaces = (relay.Node,)
        fields = ("type", "child", "guardian")

    type = graphene.Field(RelationshipTypeEnum)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return queryset.user_can_view(info.context.user).order_by("id")

    @classmethod
    @login_required
    def get_node(cls, info, id):
        try:
            return cls._meta.model.objects.user_can_view(info.context.user).get(id=id)
        except cls._meta.model.DoesNotExist:
            return None


class RelationshipInput(graphene.InputObjectType):
    type = RelationshipTypeEnum()


class GuardianInput(graphene.InputObjectType):
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    phone_number = graphene.String()
    language = LanguageEnum(required=True)
    email = graphene.String()
    languages_spoken_at_home = graphene.List(graphene.NonNull(graphene.ID))


class ChildInput(graphene.InputObjectType):
    name = graphene.String()
    birthyear = graphene.Int(required=True)
    postal_code = graphene.String(required=True)
    relationship = RelationshipInput()
    languages_spoken_at_home = graphene.List(graphene.NonNull(graphene.ID))


def validate_child_data(child_data):
    if "postal_code" in child_data:
        try:
            postal_code_validator(child_data["postal_code"])
        except ValidationError as e:
            raise DataValidationError(e.message)
    if "birthyear" in child_data:
        birthyear = child_data["birthyear"]
        if (
            child_data["birthyear"] > localdate().year
            or not Project.objects.filter(year=birthyear).exists()
        ):
            raise DataValidationError("Illegal birthyear.")
    return child_data


class SubmitChildrenAndGuardianMutation(graphene.relay.ClientIDMutation):
    class Input:
        children = graphene.List(
            graphene.NonNull(ChildInput),
            required=True,
            description="At least one child is required.",
        )
        guardian = GuardianInput(required=True)

    children = graphene.List(ChildNode)
    guardian = graphene.Field(GuardianNode)

    @classmethod
    @login_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user
        if hasattr(user, "guardian"):
            raise ApiUsageError("You have already used this mutation.")

        children_data = kwargs["children"]
        if not children_data:
            raise ApiUsageError("At least one child is required.")

        if len(children_data) > settings.KUKKUU_MAX_NUM_OF_CHILDREN_PER_GUARDIAN:
            raise MaxNumberOfChildrenPerGuardianError("Too many children.")

        guardian_data = kwargs["guardian"]
        languages_spoken_at_home = guardian_data.pop("languages_spoken_at_home", [])
        validate_guardian_data(guardian_data)
        guardian = Guardian.objects.create(
            user=user,
            first_name=guardian_data["first_name"],
            last_name=guardian_data["last_name"],
            phone_number=guardian_data.get("phone_number", ""),
            language=guardian_data["language"],
            email=guardian_data.get("email", ""),
        )
        set_obj_languages_spoken_at_home(info, guardian, languages_spoken_at_home)

        children = []
        for child_data in children_data:
            validate_child_data(child_data)

            relationship_data = child_data.pop("relationship", {})
            child_data["project_id"] = Project.objects.get(
                year=child_data["birthyear"]
            ).pk
            languages = child_data.pop("languages_spoken_at_home", [])

            child = Child.objects.create(**child_data)
            Relationship.objects.create(
                type=relationship_data.get("type"), child=child, guardian=guardian
            )
            set_obj_languages_spoken_at_home(info, child, languages)

            children.append(child)

        logger.info(
            f"user {user.uuid} submitted children {[c.pk for c in children]} "
            f"and guardian {guardian.pk}"
        )

        send_notification(
            guardian.email,
            NotificationType.SIGNUP,
            {"children": children, "guardian": guardian},
            guardian.language,
        )

        return SubmitChildrenAndGuardianMutation(children=children, guardian=guardian)


class AddChildMutation(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String()
        birthyear = graphene.Int(required=True)
        postal_code = graphene.String(required=True)
        relationship = RelationshipInput()
        languages_spoken_at_home = graphene.List(graphene.NonNull(graphene.ID))

    child = graphene.Field(ChildNode)

    @classmethod
    @login_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user
        if not hasattr(user, "guardian"):
            raise ApiUsageError(
                'You need to use "SubmitChildrenAndGuardianMutation" first.'
            )
        if (
            user.guardian.children.count()
            >= settings.KUKKUU_MAX_NUM_OF_CHILDREN_PER_GUARDIAN
        ):
            raise MaxNumberOfChildrenPerGuardianError("Too many children.")

        validate_child_data(kwargs)

        kwargs["project_id"] = Project.objects.get(year=kwargs["birthyear"]).pk
        user = info.context.user
        relationship_data = kwargs.pop("relationship", {})
        languages = kwargs.pop("languages_spoken_at_home", [])

        child = Child.objects.create(**kwargs)
        Relationship.objects.create(
            type=relationship_data.get("type"), child=child, guardian=user.guardian
        )
        set_obj_languages_spoken_at_home(info, child, languages)

        logger.info(
            f"user {user.uuid} added child {child.pk} to guardian {user.guardian.pk}"
        )

        return AddChildMutation(child=child)


class UpdateChildMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String()
        postal_code = graphene.String()
        relationship = RelationshipInput()
        languages_spoken_at_home = graphene.List(graphene.NonNull(graphene.ID))

    child = graphene.Field(ChildNode)

    @classmethod
    @login_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        validate_child_data(kwargs)
        user = info.context.user
        child_global_id = kwargs.pop("id")

        try:
            child = Child.objects.user_can_update(user).get(
                pk=from_global_id(child_global_id)[1]
            )
        except Child.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

        try:
            relationship = child.relationships.get(guardian__user=user)
            update_object(relationship, kwargs.pop("relationship", None))
        except Relationship.DoesNotExist:
            pass

        if "languages_spoken_at_home" in kwargs:
            set_obj_languages_spoken_at_home(
                info, child, kwargs.pop("languages_spoken_at_home")
            )

        update_object(child, kwargs)

        logger.info(f"user {user.uuid} updated child {child.pk}")

        return UpdateChildMutation(child=child)


class DeleteChildMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    @classmethod
    @login_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user

        try:
            child = Child.objects.user_can_delete(user).get(
                pk=from_global_id(kwargs["id"])[1]
            )
        except Child.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

        log_text = f"user {user.uuid} deleted child {child.pk}"
        child.delete()

        logger.info(log_text)

        return DeleteChildMutation()


class DjangoFilterAndOffsetConnectionField(DjangoFilterConnectionField):
    def __init__(self, type, *args, **kwargs):
        kwargs.setdefault("limit", graphene.Int())
        kwargs.setdefault("offset", graphene.Int())
        super().__init__(type, *args, **kwargs)

    @classmethod
    def connection_resolver(cls, *args, **kwargs):
        limit = kwargs.get("limit")
        has_cursor = any(arg in kwargs for arg in ("first", "last", "after", "before"))
        if limit:
            if has_cursor:
                raise ApiUsageError("Cannot use both offset and cursor pagination.")
            kwargs["first"] = limit
        return super().connection_resolver(*args, **kwargs)


class Query:
    children = DjangoFilterAndOffsetConnectionField(ChildNode, projectId=graphene.ID())
    child = relay.Node.Field(ChildNode)


class Mutation:
    submit_children_and_guardian = SubmitChildrenAndGuardianMutation.Field(
        description="This is the first mutation one needs to execute to start using "
        "the service. After that this mutation cannot be used anymore."
    )
    add_child = AddChildMutation.Field(
        description="This mutation cannot be used before one has started using the "
        'service with "SubmitChildrenAndGuardianMutation".'
    )
    update_child = UpdateChildMutation.Field()
    delete_child = DeleteChildMutation.Field()

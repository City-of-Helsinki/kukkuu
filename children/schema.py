import logging
from datetime import timedelta

import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.timezone import localtime, now
from django_ilmoitin.utils import send_notification
from graphene import relay
from graphene_django import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id
from graphql_relay.connection.arrayconnection import offset_to_cursor

from children.notifications import NotificationType
from common.schema import set_obj_languages_spoken_at_home
from common.utils import update_object
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
    available_events = relay.ConnectionField("events.schema.EventConnection")
    available_events_and_event_groups = relay.ConnectionField(
        "events.schema.EventOrEventGroupConnection"
    )
    past_events = relay.ConnectionField("events.schema.EventConnection")
    languages_spoken_at_home = DjangoConnectionField(LanguageNode)

    class Meta:
        model = Child
        interfaces = (relay.Node,)
        connection_class = ChildrenConnection
        fields = (
            "id",
            "created_at",
            "updated_at",
            "first_name",
            "last_name",
            "postal_code",
            "birthdate",
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
        return queryset.user_can_view(info.context.user).order_by(
            "last_name", "first_name", "created_at"
        )

    @classmethod
    @login_required
    def get_node(cls, info, id):
        try:
            return cls._meta.model.objects.user_can_view(info.context.user).get(id=id)
        except cls._meta.model.DoesNotExist:
            return None

    def resolve_past_events(self, info, **kwargs):
        """
        Past events include Events the user has enrolled AND the occurrence of the
        enrolment is more than KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY mins in the
        past.
        """
        events = self.project.events.user_can_view(info.context.user).published()
        past_enough_enrolled_occurrences = self.occurrences.filter(
            time__lt=timezone.now()
            - timedelta(minutes=settings.KUKKUU_ENROLLED_OCCURRENCE_IN_PAST_LEEWAY)
        )
        return events.filter(occurrences__in=past_enough_enrolled_occurrences)

    def resolve_available_events(self, info, **kwargs):
        return self.project.events.user_can_view(info.context.user).available(self)

    def resolve_available_events_and_event_groups(self, info, **kwargs):
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

    def resolve_occurrences(self, info, **kwargs):
        # Use distinct to avoid duplicated rows when querying nested occurrences
        return self.occurrences.distinct()


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
    first_name = graphene.String()
    last_name = graphene.String()
    birthdate = graphene.Date(required=True)
    postal_code = graphene.String(required=True)
    relationship = RelationshipInput()
    languages_spoken_at_home = graphene.List(graphene.NonNull(graphene.ID))


def validate_child_data(child_data):
    if "postal_code" in child_data:
        try:
            postal_code_validator(child_data["postal_code"])
        except ValidationError as e:
            raise DataValidationError(e.message)
    if "birthdate" in child_data:
        birth_year = child_data["birthdate"].year
        if (
            child_data["birthdate"] > localtime(now()).date()
            or not Project.objects.filter(year=birth_year).exists()
        ):
            raise DataValidationError("Illegal birthdate.")
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
                year=child_data["birthdate"].year
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
        first_name = graphene.String()
        last_name = graphene.String()
        birthdate = graphene.Date(required=True)
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

        kwargs["project_id"] = Project.objects.get(year=kwargs["birthdate"].year).pk
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
        first_name = graphene.String()
        last_name = graphene.String()
        birthdate = graphene.Date()
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
        has_limit_or_offset = "limit" in kwargs or "offset" in kwargs
        has_cursor = any(arg in kwargs for arg in ("first", "last", "after", "before"))

        if has_limit_or_offset:
            if has_cursor:
                raise ApiUsageError("Cannot use both offset and cursor pagination.")

            limit = kwargs.get("limit")
            if limit is not None:
                kwargs["first"] = limit
            offset = kwargs.get("offset")
            if offset is not None:
                kwargs["after"] = offset_to_cursor(offset - 1)

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

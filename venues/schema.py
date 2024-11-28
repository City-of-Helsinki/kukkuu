import logging

import graphene
from django.apps import apps
from django.db import transaction
from django.db.models import Count, Prefetch
from django.utils.translation import get_language
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from common.utils import (
    get_obj_if_user_can_administer,
    login_required,
    map_enums_to_values_in_kwargs,
    project_user_required,
    update_object_with_translations,
)
from projects.models import Project
from users.schema import LanguageEnum
from venues.models import Venue

logger = logging.getLogger(__name__)

VenueTranslation = apps.get_model("venues", "VenueTranslation")


class VenueTranslationType(DjangoObjectType):
    language_code = LanguageEnum(required=True)

    class Meta:
        model = VenueTranslation
        exclude = ("id", "master")


class VenueNode(DjangoObjectType):
    name = graphene.String()
    description = graphene.String()
    address = graphene.String()
    accessibility_info = graphene.String()
    arrival_instructions = graphene.String()
    additional_info = graphene.String()
    wc_and_facilities = graphene.String()
    www_url = graphene.String()

    class Meta:
        model = Venue
        interfaces = (relay.Node,)
        fields = (
            "id",
            "created_at",
            "updated_at",
            "name",
            "description",
            "address",
            "accessibility_info",
            "arrival_instructions",
            "additional_info",
            "wc_and_facilities",
            "www_url",
            "project",
            "translations",
            "occurrences",
        )
        filter_fields = ("project_id",)

    @classmethod
    @login_required
    # TODO: For now only logged in users can see venues
    def get_queryset(cls, queryset, info):
        lang = get_language()
        # always order venues by their name in Finnish, because that is all we need ATM
        # in Kukkuu FE and Kukkuu admin, and properly supporting ordering by the other
        # languages isn't trivial
        return (
            queryset.prefetch_related(
                Prefetch(
                    "translations",
                    queryset=VenueTranslation.objects.order_by("language_code"),
                )
            )
            .translated("fi")
            .order_by("translations__name")
            .language(lang)
        )

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return super().get_node(info, id)

    def resolve_occurrences(self, info, **kwargs):
        return (
            self.occurrences.annotate(
                enrolment_count=Count("enrolments", distinct=True)
            )
            .select_related("event")
            .order_by("time")
        )

    def resolve_translations(self, info, **kwargs):
        try:
            return self.prefetched_translations
        except AttributeError:
            return self.translations.order_by("language_code")


class VenueTranslationsInput(graphene.InputObjectType):
    name = graphene.String()
    description = graphene.String()
    language_code = LanguageEnum(required=True)
    address = graphene.String()
    accessibility_info = graphene.String()
    arrival_instructions = graphene.String()
    additional_info = graphene.String()
    www_url = graphene.String()
    wc_and_facilities = graphene.String()


class AddVenueMutation(graphene.relay.ClientIDMutation):
    class Input:
        translations = graphene.List(VenueTranslationsInput)
        project_id = graphene.GlobalID()

    venue = graphene.Field(VenueNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        kwargs["project_id"] = get_obj_if_user_can_administer(
            info, kwargs["project_id"], Project
        ).pk
        venue = Venue.objects.create_translatable_object(**kwargs)

        logger.info(
            f"user {info.context.user.uuid} added venue {venue} with data {kwargs}"
        )

        return AddVenueMutation(venue=venue)


class UpdateVenueMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()
        translations = graphene.List(VenueTranslationsInput)
        project_id = graphene.GlobalID(required=False)

    venue = graphene.Field(VenueNode)

    @classmethod
    @project_user_required
    @transaction.atomic
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        project_global_id = kwargs.pop("project_id", None)
        if project_global_id:
            kwargs["project_id"] = get_obj_if_user_can_administer(
                info, project_global_id, Project
            )
        venue = get_obj_if_user_can_administer(info, kwargs.pop("id"), Venue)
        update_object_with_translations(venue, kwargs)

        logger.info(
            f"user {info.context.user.uuid} updated venue {venue} with data {kwargs}"
        )

        return UpdateVenueMutation(venue=venue)


class DeleteVenueMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    @classmethod
    @project_user_required
    @transaction.atomic
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        venue = get_obj_if_user_can_administer(info, kwargs["id"], Venue)
        log_text = f"user {info.context.user.uuid} deleted venue {venue}"
        venue.delete()

        logger.info(log_text)

        return DeleteVenueMutation()


class Query:
    venue = relay.Node.Field(VenueNode)
    venues = DjangoFilterConnectionField(VenueNode)


class Mutation:
    add_venue = AddVenueMutation.Field()
    update_venue = UpdateVenueMutation.Field()
    delete_venue = DeleteVenueMutation.Field()

import graphene
from django.apps import apps
from django.db import transaction
from django.db.models import Count
from django.utils.translation import get_language
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphql_jwt.decorators import login_required, staff_member_required
from graphql_relay import from_global_id

from common.utils import update_object_with_translations
from kukkuu.exceptions import KukkuuGraphQLError
from users.schema import LanguageEnum
from venues.models import Venue

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

    @classmethod
    @login_required
    # TODO: For now only logged in users can see venues
    def get_queryset(cls, queryset, info):
        lang = get_language()
        return queryset.order_by("-created_at").language(lang)

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return super().get_node(info, id)

    def resolve_occurrences(self, info, **kwargs):
        return (
            self.occurrences.annotate(
                enrolments_count=Count("enrolments", distinct=True)
            )
            .select_related("event")
            .order_by("time")
        )


class VenueTranslationsInput(graphene.InputObjectType):
    name = graphene.String(required=True)
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

    venue = graphene.Field(VenueNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Add validation
        venue = Venue.objects.create_translatable_object(**kwargs)
        return AddVenueMutation(venue=venue)


class UpdateVenueMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID(required=True)
        translations = graphene.List(VenueTranslationsInput)
        delete_translations = graphene.List(LanguageEnum)

    venue = graphene.Field(VenueNode)

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Add validation
        venue_global_id = kwargs.pop("id")
        try:
            venue = Venue.objects.get(pk=from_global_id(venue_global_id)[1])
            update_object_with_translations(venue, kwargs)
        except Venue.DoesNotExist as e:
            raise KukkuuGraphQLError(e)
        return UpdateVenueMutation(venue=venue)


class DeleteVenueMutation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.GlobalID()

    @classmethod
    @staff_member_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # TODO: Validate data
        venue_id = from_global_id(kwargs["id"])[1]
        try:
            venue = Venue.objects.get(pk=venue_id)
            venue.delete()
        except Venue.DoesNotExist as e:
            raise KukkuuGraphQLError(e)
        return DeleteVenueMutation()


class Query:
    venue = relay.Node.Field(VenueNode)
    venues = DjangoConnectionField(VenueNode)


class Mutation:
    add_venue = AddVenueMutation.Field()
    update_venue = UpdateVenueMutation.Field()
    delete_venue = DeleteVenueMutation.Field()

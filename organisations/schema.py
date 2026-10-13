import graphene
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from common.utils import login_required
from organisations.models import Organisation


class OrganisationNode(DjangoObjectType):
    class Meta:
        model = Organisation
        interfaces = (relay.Node,)
        fields = (
            "id",
            "name",
            "created_at",
            "updated_at",
        )

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        user = info.context.user
        # Only event organisers (system admins and project admins) should be able
        # to query organisations.
        # Regular public UI users logging in with Helsinki-Profile cannot see the list
        # of companies.
        if not user.is_event_organiser:
            return queryset.none()
        return queryset.user_can_view(user)


class Query(graphene.ObjectType):
    organisations = DjangoConnectionField(OrganisationNode)
    organisation = relay.Node.Field(OrganisationNode)

    @login_required
    def resolve_organisations(self, info, **kwargs):
        user = info.context.user
        # Restrict endpoint to event organisers (staff/project admins) only
        if not user.is_event_organiser:
            return Organisation.objects.none()
        return Organisation.objects.user_can_view(user)

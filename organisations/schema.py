import graphene
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from common.utils import login_required
from organisations.models import Organisation


class OrganisationNode(DjangoObjectType):
    class Meta:
        model = Organisation
        interfaces = (relay.Node,)
        # Ensure 'events' is NOT exposed on this node to prevent unauthorized event
        # scraping
        exclude = ("events",)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        user = info.context.user
        # Only system admins and users who can administer some project should be able
        # to query organisations.
        # Regular public UI users logging in with Helsinki-Profile cannot see the list
        # of companies.
        if not (user.is_system_administrator or user.administered_projects.exists()):
            return queryset.none()
        return queryset.user_can_view(user)


class Query(graphene.ObjectType):
    organisations = DjangoConnectionField(OrganisationNode)

    @login_required
    def resolve_organisations(self, info, **kwargs):
        user = info.context.user
        # Restrict endpoint to admins (staff/project admins) only
        if not (user.is_system_administrator or user.administered_projects.exists()):
            return Organisation.objects.none()
        return Organisation.objects.user_can_view(user)

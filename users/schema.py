import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import transaction
from graphene import relay
from graphene_django import DjangoConnectionField
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from common.schema import LanguageEnum
from common.utils import update_object
from kukkuu.exceptions import InvalidEmailFormatError, ObjectDoesNotExistError

from .models import Guardian

User = get_user_model()


def validate_guardian_data(guardian_data):
    if "email" in guardian_data:
        try:
            EmailValidator()(guardian_data["email"])
        except ValidationError:
            raise InvalidEmailFormatError("Invalid email format")
    return guardian_data


class GuardianNode(DjangoObjectType):
    language = LanguageEnum(required=True)
    email = graphene.String()

    class Meta:
        model = Guardian
        interfaces = (relay.Node,)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.user_can_view(info.context.user).order_by("last_name")

    def resolve_email(self, info, **kwargs):
        return self.get_email_in_use()


class AdminNode(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (relay.Node,)
        fields = ("projects",)


class UpdateMyProfileMutation(graphene.relay.ClientIDMutation):
    class Input:
        first_name = graphene.String()
        last_name = graphene.String()
        phone_number = graphene.String()
        language = LanguageEnum()
        email = graphene.String()

    my_profile = graphene.Field(GuardianNode)

    @classmethod
    @login_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user

        try:
            guardian = user.guardian
        except Guardian.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

        validate_guardian_data(kwargs)
        update_object(guardian, kwargs)

        guardian.email = guardian.get_email_in_use()
        return UpdateMyProfileMutation(my_profile=guardian)


class Query:
    guardians = DjangoConnectionField(GuardianNode)
    my_profile = graphene.Field(GuardianNode)
    my_admin_profile = graphene.Field(AdminNode)

    @staticmethod
    @login_required
    def resolve_guardians(parent, info, **kwargs):
        return Guardian.objects.user_can_view(info.context.user)

    @staticmethod
    @login_required
    def resolve_my_profile(parent, info, **kwargs):
        return Guardian.objects.filter(user=info.context.user).first()

    @staticmethod
    @login_required
    def resolve_my_admin_profile(parent, info, **kwargs):
        return info.context.user


class Mutation:
    update_my_profile = UpdateMyProfileMutation.Field()

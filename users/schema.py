import graphene
from django.contrib.auth import get_user_model
from django.db import transaction
from graphene import relay
from graphene_django import DjangoConnectionField
from graphene_django.types import DjangoObjectType

from common.schema import LanguageEnum, set_obj_languages_spoken_at_home
from common.utils import login_required, update_object
from kukkuu.exceptions import ObjectDoesNotExistError
from projects.schema import ProjectNode

from .models import Guardian
from .utils import (
    send_guardian_email_changed_notification,
    send_guardian_email_update_token_notification,
    validate_email_verification_token,
    validate_guardian_data,
    validate_guardian_email,
)

User = get_user_model()


class GuardianNode(DjangoObjectType):
    language = LanguageEnum(required=True)

    class Meta:
        model = Guardian
        fields = (
            "id",
            "created_at",
            "updated_at",
            "user",
            "first_name",
            "last_name",
            "phone_number",
            "language",
            "email",
            "children",
            "relationships",
            "languages_spoken_at_home",
        )
        interfaces = (relay.Node,)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.user_can_view(info.context.user).order_by("last_name")


class AdminNode(DjangoObjectType):
    projects = DjangoConnectionField(ProjectNode)

    class Meta:
        model = User
        interfaces = (relay.Node,)
        fields = ("projects", "username", "email")

    @staticmethod
    def resolve_projects(parent, info, **kwargs):
        return parent.administered_projects


class UpdateMyProfileMutation(graphene.relay.ClientIDMutation):
    class Input:
        first_name = graphene.String()
        last_name = graphene.String()
        phone_number = graphene.String()
        language = LanguageEnum()
        languages_spoken_at_home = graphene.List(graphene.NonNull(graphene.ID))

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

        languages_spoken_at_home = kwargs.pop("languages_spoken_at_home", [])
        validate_guardian_data(
            kwargs
        )  # NOTE: doesn't actually do anything, since it validates only an email.

        update_object(guardian, kwargs)
        set_obj_languages_spoken_at_home(info, guardian, languages_spoken_at_home)

        return UpdateMyProfileMutation(my_profile=guardian)


class UpdateMyEmailMutation(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)
        verification_token = graphene.String(required=True)

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

        verification_token = kwargs["verification_token"]
        new_email = kwargs["email"]
        old_email = guardian.email

        # Validate
        validate_guardian_email(new_email)
        validate_email_verification_token(user, new_email, verification_token)

        # Set new value
        guardian.email = new_email

        # Save and send message
        if guardian.email != old_email:
            guardian.save()
            send_guardian_email_changed_notification(guardian)

        return UpdateMyEmailMutation(my_profile=guardian)


class RequestEmailUpdateTokenMutation(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)

    email_update_token_requested = graphene.Boolean()
    email = graphene.String()

    @classmethod
    @login_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **kwargs):
        new_email = kwargs["email"]
        user = info.context.user
        try:
            guardian = user.guardian
        except Guardian.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

        verification_token = user.deactivate_and_create_email_verification_token(
            new_email
        )
        send_guardian_email_update_token_notification(
            guardian, new_email, verification_token.key
        )

        return RequestEmailUpdateTokenMutation(
            email_update_token_requested=True,
            email=new_email,
        )


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
    update_my_email = UpdateMyEmailMutation.Field()
    request_email_update_token = RequestEmailUpdateTokenMutation.Field()

import graphene
from auditlog_extra.graphene_decorators import auditlog_access
from django.contrib.auth import get_user_model
from django.db import transaction
from graphene import relay
from graphene_django import DjangoConnectionField
from graphene_django.types import DjangoObjectType

from common.schema import LanguageEnum, set_obj_languages_spoken_at_home
from common.utils import login_required, map_enums_to_values_in_kwargs, update_object
from kukkuu.exceptions import ObjectDoesNotExistError
from projects.schema import ProjectNode
from verification_tokens.decorators import user_from_auth_verification_token

from .models import Guardian
from .services import GuardianEmailChangeNotificationService
from .utils import (
    validate_email_verification_token,
    validate_guardian_data,
    validate_guardian_email,
)

User = get_user_model()


@auditlog_access
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
            "language",
            "phone_number",
            "email",
            "has_accepted_communication",
            "children",
            "relationships",
            "languages_spoken_at_home",
        )
        interfaces = (relay.Node,)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.user_can_view(info.context.user).order_by("last_name")

    @staticmethod
    def resolve_phone_number(guardian: Guardian, info) -> str:
        if not guardian.user_can_view_contact_info(info.context.user):
            return ""
        return guardian.phone_number

    @staticmethod
    def resolve_email(guardian: Guardian, info) -> str:
        if not guardian.user_can_view_contact_info(info.context.user):
            return ""
        return guardian.email


class GuardianCommunicationSubscriptionsNode(DjangoObjectType):
    class Meta:
        model = Guardian
        fields = (
            "id",
            "first_name",
            "last_name",
            "language",
            "has_accepted_communication",
        )
        # Skip the registry, or this GuardianCommunicationSubscriptionsNode
        # would overlap with the GuardianNode, which would then lead to
        # situations where a wrong node type is used in wrong places.
        skip_registry = True
        interfaces = (relay.Node,)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.user_can_view(info.context.user)


@auditlog_access
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
        has_accepted_communication = graphene.Boolean()

    my_profile = graphene.Field(GuardianNode)

    @classmethod
    @login_required
    @transaction.atomic
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user

        try:
            guardian = user.guardian
        except Guardian.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

        should_update_languages_spoken_at_home = "languages_spoken_at_home" in kwargs
        languages_spoken_at_home = kwargs.pop("languages_spoken_at_home", [])

        validate_guardian_data(
            kwargs
        )  # NOTE: doesn't actually do anything, since it validates only an email.

        update_object(guardian, kwargs)

        if should_update_languages_spoken_at_home:
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
    @map_enums_to_values_in_kwargs
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
            GuardianEmailChangeNotificationService.send_email_changed_notification(
                guardian
            )

        return UpdateMyEmailMutation(my_profile=guardian)


class RequestEmailUpdateTokenMutation(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)

    email_update_token_requested = graphene.Boolean()
    email = graphene.String()

    @classmethod
    @login_required
    @transaction.atomic
    @map_enums_to_values_in_kwargs
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
        GuardianEmailChangeNotificationService.send_email_update_token_notification(
            guardian, new_email, verification_token.key
        )

        return RequestEmailUpdateTokenMutation(
            email_update_token_requested=True,
            email=new_email,
        )


class UpdateMyCommunicationSubscriptionsMutation(graphene.relay.ClientIDMutation):
    class Input:
        has_accepted_communication = graphene.Boolean(required=True)
        auth_token = graphene.String(
            description="Auth token can be used to authorize the action "
            "without logging in as a user."
        )

    guardian = graphene.Field(GuardianCommunicationSubscriptionsNode)

    @classmethod
    # When the login_required raises a PermissionDenied exception,
    # use the auth_token from the input variables
    # to populate the context.user with the token related user
    # and then try again.
    @user_from_auth_verification_token(
        get_token=lambda variables: variables.get("auth_token", None),
        use_only_when_first_denied=True,
    )
    @login_required
    @map_enums_to_values_in_kwargs
    def mutate_and_get_payload(cls, root, info, has_accepted_communication, **kwargs):
        user = info.context.user
        try:
            guardian = user.guardian
        except Guardian.DoesNotExist as e:
            raise ObjectDoesNotExistError(e)

        guardian.has_accepted_communication = has_accepted_communication
        guardian.save()

        return UpdateMyCommunicationSubscriptionsMutation(guardian=guardian)


class Query:
    guardians = DjangoConnectionField(GuardianNode)
    my_profile = graphene.Field(GuardianNode)
    my_admin_profile = graphene.Field(AdminNode)
    my_communication_subscriptions = graphene.Field(
        GuardianCommunicationSubscriptionsNode,
        auth_token=graphene.String(
            description="Auth token can be used to authorize the action "
            "without logging in as a user."
        ),
    )

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

    @staticmethod
    # When the login_required raises a PermissionDenied exception,
    # use the auth_token from the input variables
    # to populate the context.user with the token related user
    # and then try again.
    @user_from_auth_verification_token(
        get_token=lambda variables: variables.get("auth_token", None),
        use_only_when_first_denied=True,
    )
    @login_required
    def resolve_my_communication_subscriptions(parent, info, **kwargs):
        return info.context.user.guardian


class Mutation:
    update_my_profile = UpdateMyProfileMutation.Field()
    update_my_email = UpdateMyEmailMutation.Field()
    request_email_update_token = RequestEmailUpdateTokenMutation.Field()
    update_my_communication_subscriptions = (
        UpdateMyCommunicationSubscriptionsMutation.Field()
    )

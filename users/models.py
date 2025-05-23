import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager as OriginalUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from guardian.shortcuts import get_objects_for_user
from helsinki_gdpr.models import SerializableMixin
from helusers.models import AbstractUser

from common.models import TimestampedModel, UUIDPrimaryKeyModel
from events.consts import notification_types_that_need_communication_acceptance
from gdpr.consts import CLEARED_VALUE
from gdpr.models import GDPRModel
from languages.models import Language
from projects.models import ProjectPermission

if TYPE_CHECKING:
    from children.models import Child
    from projects.models import Project
    from subscriptions.models import FreeSpotNotificationSubscription
    from verification_tokens.models import VerificationToken

logger = logging.getLogger(__name__)


class UserQuerySet(models.QuerySet):
    def possible_admins(self):
        # This filtering isn't perfect because
        #   1) it is possible there are a few normal users without a Guardian object
        #   2) this prevents using the same user account for Kukkuu UI and Kukkuu admin
        #      which was convenient in dev/testing, and might be a valid case in
        #      production as well in the future
        # but for now this should be easily good enough.
        return self.filter(guardian=None)


# This is needed when using a custom User queryset
class UserManager(
    OriginalUserManager.from_queryset(UserQuerySet),
    SerializableMixin.SerializableManager,
):
    pass


class User(AbstractUser, GDPRModel, SerializableMixin):
    serialize_fields = (
        {"name": "uuid", "accessor": lambda uuid: str(uuid)},
        {"name": "username"},
        {"name": "first_name"},
        {"name": "last_name"},
        {"name": "email"},
        {
            "name": "administered_projects",
            "accessor": lambda projects: [p.serialize() for p in projects],
        },
        {"name": "last_login", "accessor": lambda t: t.isoformat() if t else None},
        {"name": "date_joined", "accessor": lambda t: t.isoformat() if t else None},
        {"name": "guardian"},
    )

    # NOTE: `is_obsolete` is deprecated after the migration process
    # that deactivates the obsoleted users (`0014_deactivate_obsolete_users.py`).
    # When Tunnistamo was changed to a Keycloak service,
    # the field has been used to mark the users that are not anymore
    # accessible, but are still in the database and need to receive
    # notifications (like emails). The users are not deleted, because
    # they might have children or other objects linked to them and
    # it was important that they were not deactivated or deleted,
    # but just set as unaccessible by the auth service migration process.
    #
    # The `is_active` field is used to mark the users that are
    # not anymore able to log in to the system and the `is_obsolete`
    # users should be deactivated at some point, which then makes this
    # field needless as well.
    is_obsolete = models.BooleanField(
        _("obsoleted"),
        null=False,
        default=False,
        help_text=_(
            "Designates whether the user account is obsoleted "
            "and cannot be anymore accessed, "
            "e.g. after an auth service change process "
            "(when Tunnistamo is changed to a Keycloak service)."
        ),
    )

    objects = UserManager()

    gdpr_sensitive_data_fields = ["first_name", "last_name", "email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return super().__str__() or self.username

    def get_users_projects_with_permission(
        self, permission: ProjectPermission
    ) -> list["Project"]:
        """
        Get all projects where the user has the given permission.
        """
        from projects.models import Project

        return list(get_objects_for_user(self, permission.value, Project))

    @cached_property
    def administered_projects(self) -> list["Project"]:
        return self.get_users_projects_with_permission(ProjectPermission.ADMIN)

    @property
    def projects_with_family_data_access(self) -> list["Project"]:
        return self.get_users_projects_with_permission(ProjectPermission.VIEW_FAMILIES)

    def has_global_permission(self, project_permission: ProjectPermission) -> bool:
        return self.has_perm(project_permission.permission_name)

    def has_project_permission(
        self, project_permission: ProjectPermission, project: "Project"
    ) -> bool:
        return self.has_perm(
            project_permission.value, project
        ) or self.has_global_permission(project_permission)

    def can_administer_project(self, project: "Project") -> bool:
        return project in self.administered_projects

    def can_publish_in_project(self, project: "Project") -> bool:
        return self.has_project_permission(ProjectPermission.PUBLISH, project)

    def can_manage_event_groups_in_project(self, project: "Project") -> bool:
        return self.has_project_permission(
            ProjectPermission.MANAGE_EVENT_GROUPS, project
        )

    def can_send_messages_to_all_in_project(self, project: "Project") -> bool:
        return self.has_project_permission(
            ProjectPermission.SEND_MESSAGE_TO_ALL_IN_PROJECT, project
        )

    def can_view_families_in_project(self, project: "Project") -> bool:
        return self.has_project_permission(ProjectPermission.VIEW_FAMILIES, project)

    def get_active_verification_tokens(
        self, verification_type: Optional[str] = None
    ) -> list["VerificationToken"]:
        """Filter active verification tokens"""
        from verification_tokens.models import VerificationToken

        return VerificationToken.objects.filter_active_tokens(
            self, verification_type=verification_type, user=self
        )

    def deactivate_and_create_email_verification_token(
        self, email: str
    ) -> "VerificationToken":
        from verification_tokens.models import VerificationToken

        return VerificationToken.objects.deactivate_and_create_token(
            self,
            self,
            VerificationToken.VERIFICATION_TYPE_EMAIL_VERIFICATION,
            email,
        )

    def get_subscriptions(
        self, child: Optional["Child"] = None
    ) -> Union[models.QuerySet, list["FreeSpotNotificationSubscription"]]:
        """
        Get all the user's subscriptions.
        If a child argument is given, only the subscriptions that are linked
        to that given child are returned.
        """
        from subscriptions.models import FreeSpotNotificationSubscription

        return FreeSpotNotificationSubscription.objects.user_subscriptions(self, child)

    def unsubscribe_all_notification_subscriptions(
        self, child: Optional["Child"] = None
    ):
        """
        Unsubscribe user's all notification subsriptions.
        If a child argument is given, the unsubscribing is done only
        to subscriptions that are linked to the given child that
        the user is a guardian to.

        NOTE: This function deletes the FreeSpotNotifications, which are linked to
        a Child and Occurrence instances. **It should be noted that the current
        model architecture allows that a child can have multiple guardians,
        so unsubscribe can delete some notifications from other users as well.
        However, the UI apps has never allowed more than 1 guardian for a child.**
        """
        subscriptions = self.get_subscriptions(child=child)
        count = subscriptions.count()
        subscriptions.delete()
        logger.info(
            f"User {self.uuid} unsubscribed all ({count}) "
            "subscriptions they had active%s"
            % (f" for child {child.id}." if child else ".")
        )
        return count

    def create_subscriptions_management_auth_token(self):
        """
        Create a new token that has an expiration date
        and can be used to as an authorization token to manage
        the user's subscriptions to notifications.
        """
        from verification_tokens.models import VerificationToken

        # NOTE: Should the email be left empty?
        # The only value the email gives here is that it is denormalized to db
        try:
            email = self.guardian.email
            if not email:
                email = self.email
        except ObjectDoesNotExist:
            email = self.email

        # NOTE: Should this get_or_create never expiring tokens instead?
        # It would be worse in security perspective, because 1 token would
        # serve forever, but it would be better in usability, because
        # then the token would be the same in every email every time, forever.
        return VerificationToken.objects.create_token(
            self,
            self,
            VerificationToken.VERIFICATION_TYPE_SUBSCRIPTIONS_AUTH,
            email=email,
            expiry_minutes=settings.SUBSCRIPTIONS_AUTH_TOKEN_VALID_MINUTES,
            token_length=settings.SUBSCRIPTIONS_AUTH_TOKEN_LENGTH,
        )

    def clear_gdpr_sensitive_data_fields(self):
        super().clear_gdpr_sensitive_data_fields()
        self.is_active = False
        self.username = f"{CLEARED_VALUE}-{self.uuid}"
        self.set_unusable_password()
        self.save()


class GuardianQuerySet(models.QuerySet):
    def user_can_view(self, user: User):
        return self.filter(
            Q(user=user) | Q(children__project__in=user.administered_projects)
        ).distinct()

    @transaction.atomic()
    def delete(self):
        for child in self:
            child.delete()

    def has_accepted_communication_for_notification(self, notification_type: str):
        """Filters guardians who have accepted communication for the given notification
        type.

        Initially, the queryset is filtered to include only **active**
        (`user__is_active=True`) and **non-obsolete** (`is_obsolete=False`) guardians.
        If the `notification_type` requires explicit acceptance (i.e., it is found
        within `notification_types_that_need_communication_acceptance`), the queryset
        will be further filtered to include only guardians for whom
        `has_accepted_communication` is True.

        Args:
            notification_type (str): The type of notification. This should be one of the
                `NotificationType` constant string literals.

        Returns:
            GuardianQuerySet: A filtered queryset of guardians if the
                `notification_type` requires acceptance; otherwise, returns
                the initially filtered queryset (active and non-obsolete guardians).
        """
        queryset = self.filter(user__is_active=True, user__is_obsolete=False)
        if (
            notification_type
            not in notification_types_that_need_communication_acceptance
        ):
            return queryset
        return queryset.filter(has_accepted_communication=True)

    def for_auth_service_is_changing_notification(
        self,
        user_joined_before: Optional[datetime] = None,
        obsoleted_users_only=True,
        guardian_emails: Optional[list[str]] = None,
    ):
        if user_joined_before and user_joined_before > timezone.now():
            raise ValueError("The user_joined_before cannot be set in future.")

        qs_filters = {"user__date_joined__lte": (user_joined_before or timezone.now())}
        if obsoleted_users_only:
            qs_filters.update({"user__is_obsolete": True})
        if guardian_emails:
            qs_filters.update({"email__in": guardian_emails})
        return self.filter(**qs_filters)


class Guardian(GDPRModel, UUIDPrimaryKeyModel, TimestampedModel, SerializableMixin):
    user = models.OneToOneField(
        get_user_model(), verbose_name=_("user"), on_delete=models.CASCADE
    )
    first_name = models.CharField(verbose_name=_("first name"), max_length=64)
    last_name = models.CharField(verbose_name=_("last name"), max_length=64)
    phone_number = models.CharField(
        verbose_name=_("phone number"), max_length=64, blank=True
    )
    language = models.CharField(
        verbose_name=_("language"), max_length=10, default=settings.LANGUAGE_CODE
    )
    email = models.EmailField(
        _("email address"),
        blank=True,
        help_text=_("If left blank, will be populated with the user's email."),
    )
    languages_spoken_at_home = models.ManyToManyField(
        Language,
        verbose_name=_("languages spoken at home"),
        related_name="guardians",
        blank=True,
    )
    # NOTE: All guardians are initialized to have has_accepted_communication=True
    # in users/migrations/0013_replace_has_accepted_marketing_with_communication.py,
    # before they have implicitly accepted it when they have created an account.
    has_accepted_communication = models.BooleanField(
        _("accepts communication"), null=False, default=False
    )

    serialize_fields = (
        {"name": "id", "accessor": lambda uuid: str(uuid)},
        {"name": "user", "accessor": lambda u: str(u)},
        {"name": "first_name"},
        {"name": "last_name"},
        {"name": "email"},
        {"name": "phone_number"},
        {"name": "has_accepted_communication"},
        {"name": "children"},
    )

    objects = SerializableMixin.SerializableManager.from_queryset(GuardianQuerySet)()

    gdpr_sensitive_data_fields = ["first_name", "last_name", "phone_number", "email"]

    class Meta:
        verbose_name = _("guardian")
        verbose_name_plural = _("guardians")
        ordering = ["-created_at", "last_name", "first_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def save(self, *args, **kwargs):
        if not self.email:
            self.email = self.user.email
        super().save(*args, **kwargs)

    @transaction.atomic()
    def delete(self, *args, **kwargs):
        for child in self.children.all():
            if child.guardians.count() == 1:
                child.delete()
        return super().delete(*args, **kwargs)

    def user_can_view_contact_info(self, user: User) -> bool:
        return (
            self.user == user
            or user.has_global_permission(ProjectPermission.VIEW_FAMILIES)
            or any(
                user.can_view_families_in_project(child.project)
                for child in self.children.all()
            )
        )

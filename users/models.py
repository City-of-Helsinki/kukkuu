import logging
from typing import Optional, TYPE_CHECKING, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager as OriginalUserManager
from django.db import models, transaction
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from guardian.shortcuts import get_objects_for_user
from helusers.models import AbstractUser

from common.models import TimestampedModel, UUIDPrimaryKeyModel
from languages.models import Language

if TYPE_CHECKING:
    from children.models import Child
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
class UserManager(OriginalUserManager.from_queryset(UserQuerySet)):
    pass


class User(AbstractUser):
    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return super().__str__() or self.username

    @cached_property
    def administered_projects(self):
        from projects.models import Project  # noqa

        return list(get_objects_for_user(self, "admin", Project))

    def can_administer_project(self, project):
        return project in self.administered_projects

    def can_publish_in_project(self, project):
        return self.has_perm("publish", project) or self.has_perm("projects.publish")

    def can_manage_event_groups_in_project(self, project):
        return self.has_perm("manage_event_groups", project) or self.has_perm(
            "projects.manage_event_groups"
        )

    def get_active_verification_tokens(
        self, verification_type: "VerificationToken.verification_type" = None
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
        except Guardian.DoesNotExist:
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
            expiry_minutes=getattr(
                settings, "SUBSCRIPTIONS_AUTH_TOKEN_VALID_MINUTES", 30 * 24 * 60
            ),  # 30 days
            token_length=getattr(settings, "SUBSCRIPTIONS_AUTH_TOKEN_LENGTH", 16),
        )


class GuardianQuerySet(models.QuerySet):
    def user_can_view(self, user):
        return self.filter(
            Q(user=user) | Q(children__project__in=user.administered_projects)
        ).distinct()

    @transaction.atomic()
    def delete(self):
        for child in self:
            child.delete()


class Guardian(UUIDPrimaryKeyModel, TimestampedModel):
    user = models.OneToOneField(
        get_user_model(), verbose_name=_("user"), on_delete=models.CASCADE
    )
    first_name = models.CharField(verbose_name=_("first name"), max_length=64)
    last_name = models.CharField(verbose_name=_("last name"), max_length=64)
    phone_number = models.CharField(
        verbose_name=_("phone number"), max_length=64, blank=True
    )
    language = models.CharField(
        verbose_name=_("language"), max_length=10, default=settings.LANGUAGES[0][0]
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
    has_accepted_marketing = models.BooleanField(
        _("accepts marketing"), null=False, default=False
    )

    objects = GuardianQuerySet.as_manager()

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

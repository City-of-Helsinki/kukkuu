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

    objects = GuardianQuerySet.as_manager()

    class Meta:
        verbose_name = _("guardian")
        verbose_name_plural = _("guardians")
        ordering = ["-created_at", "last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

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

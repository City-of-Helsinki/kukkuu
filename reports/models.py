from django.db import models
from django.utils.translation import gettext_lazy as _

ACCESS_REPORT_API_PERM = "reports.access_report_api"


class Permission(models.Model):
    """Non-db model just for holding reports' permissions.

    Needed because all Django's permissions need to be tied to a Model/ContentType.
    """

    class Meta:
        managed = False
        default_permissions = []
        permissions = [
            (ACCESS_REPORT_API_PERM.split(".")[1], _("Can access report API"))
        ]

    @classmethod
    def get_codenames(cls):
        return [codename for codename, _ in cls._meta.permissions]

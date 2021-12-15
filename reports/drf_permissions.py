from rest_framework.permissions import BasePermission

from reports.models import ACCESS_REPORT_API_PERM


class ReportAPIPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm(ACCESS_REPORT_API_PERM)

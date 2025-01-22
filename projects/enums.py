from enum import Enum


class ProjectPermission(Enum):
    ADMIN = "admin"
    PUBLISH = "publish"
    MANAGE_EVENT_GROUPS = "manage_event_groups"
    SEND_MESSAGE_TO_ALL_IN_PROJECT = "can_send_to_all_in_project"
    VIEW_FAMILIES = "view_families"

    @staticmethod
    def get_project_permission_name(permission: str) -> str:
        """
        Project permission name for the given permission,
        basically just prefixes the given string with "projects.".

        :return: Given permission prefixed with "projects.",
                 e.g. "projects.admin" for input "admin".
        """
        return f"projects.{permission}"

    @property
    def permission_name(self):
        """
        Permission name for this project permission.

        Example:
            ProjectPermission.ADMIN.permission_name == "projects.admin"
        """
        return self.get_project_permission_name(self.value)

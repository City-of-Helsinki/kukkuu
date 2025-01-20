def project_permission_name(permission: str) -> str:
    """
    Permission name for a project permission.

    Example:
        project_permission_name(ProjectPermission.ADMIN.value) == "projects.admin"
    """
    return f"projects.{permission}"

import logging

from django.apps import AppConfig
from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_migrate
from django.utils import translation

logger = logging.getLogger(__name__)


def _get_or_create_browser_test_group():
    """
    Gets or creates the Group object for browser tests.

    Returns:
        Group: The retrieved or created Group instance.
    """
    from django.contrib.auth.models import Group

    # Group
    group, _ = Group.objects.get_or_create(name=settings.BROWSER_TEST_GROUP_NAME)
    logger.info(f"Group '{group}' retrieved or created.")
    return group


def _get_or_create_browser_test_ad_group():
    """
    Gets or creates the ADGroup object for browser tests.

    Returns:
        ADGroup: The retrieved or created ADGroup instance.
    """
    from helusers.models import ADGroup

    # ADGroup (lowercase name and display_name)
    ad_group_name = settings.BROWSER_TEST_AD_GROUP_NAME.lower()
    ad_group, _ = ADGroup.objects.get_or_create(
        name=ad_group_name, defaults={"display_name": ad_group_name}
    )
    logger.info(f"ADGroup '{ad_group}' retrieved or created.")
    return ad_group


def _get_or_create_browser_test_ad_group_mapping(ad_group, group):
    """
    Gets or creates the ADGroupMapping object for browser tests,
    linking the given ADGroup and Group.

    Args:
        ad_group (ADGroup): The ADGroup instance to link.
        group (Group): The Group instance to link.

    Returns:
        ADGroupMapping: The retrieved or created ADGroupMapping instance.
    """
    from helusers.models import ADGroupMapping

    # ADGroupMapping
    ad_group_mapping, _ = ADGroupMapping.objects.get_or_create(
        ad_group=ad_group, group=group
    )
    logger.info(f"ADGroupMapping '{ad_group_mapping}' retrieved or created.")
    return ad_group_mapping


def _get_or_create_browser_test_project():
    """
    Gets or creates the Project object for browser tests,
    ensuring the correct translated name.

    Returns:
        Project: The retrieved or created Project instance.
    """
    from projects.models import Project

    # Activate default language before accessing translated fields
    translation.activate(settings.LANGUAGE_CODE)

    try:
        # Project (check for name updates)
        project, _ = Project.objects.get_or_create(
            year=settings.BROWSER_TEST_PROJECT_YEAR,
            defaults={"translation__name": settings.BROWSER_TEST_PROJECT_NAME},
        )
        logger.info(f"Project '{project}' retrieved or created.")

        return project

    finally:
        # Deactivate language after using translated fields
        translation.deactivate()


def _set_group_project_permissions(project, group):
    """
    Assigns the required project permissions to the given Group
    for the specified Project.

    Args:
        project (Project): The Project instance to assign permissions for.
        group (Group): The Group to which permissions should be granted.
    """
    from guardian.shortcuts import assign_perm

    from projects.models import Project

    project_perms = [
        f"projects.{project_perm[0]}" for project_perm in Project._meta.permissions
    ]
    for perm in project_perms:
        try:
            assign_perm(perm, group, project)
            logger.info(
                f"Assigned permission '{perm}' to project {project} for group {group}."
            )
        except Exception as e:  # Catch specific permission-related exceptions
            logger.error(f"Error assigning permission '{perm}': {e}")


@transaction.atomic()
def create_browser_test_resources(sender, **kwargs):
    """Creates Group, ADGroup, and Project resources for browser tests."""

    if not settings.OIDC_BROWSER_TEST_API_TOKEN_AUTH["ENABLED"]:
        return

    group = _get_or_create_browser_test_group()
    ad_group = _get_or_create_browser_test_ad_group()
    _get_or_create_browser_test_ad_group_mapping(ad_group=ad_group, group=group)
    project = _get_or_create_browser_test_project()

    _set_group_project_permissions(project=project, group=group)


class ProjectsConfig(AppConfig):
    name = "projects"

    def ready(self):
        post_migrate.connect(create_browser_test_resources, sender=self)

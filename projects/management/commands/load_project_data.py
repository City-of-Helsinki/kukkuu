from auditlog.context import disable_auditlog
from django.apps import apps
from django.core.management.base import BaseCommand

from projects.consts import PROJECTS_DATA


class Command(BaseCommand):
    help = (
        "Load default project data into the database. "
        "There should be a project for each year after year 2020, "
        "so the children who have that birth year can be enrolled in the project. "
        "Each project is created or updated with translations. "
    )

    def handle(self, *args, **kwargs):
        Project = apps.get_model("projects", "Project")

        with disable_auditlog():
            for project_data in PROJECTS_DATA:
                project, created = Project.objects.get_or_create(
                    year=project_data["year"]
                )
                for lang_code, name in project_data["translations"].items():
                    project.set_current_language(lang_code)
                    project.name = name
                    project.save()

        self.stdout.write(self.style.SUCCESS("Successfully loaded project data"))

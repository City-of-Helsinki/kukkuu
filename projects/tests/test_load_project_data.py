import pytest
from django.core.management import call_command

from projects.consts import PROJECTS_DATA
from projects.models import Project


@pytest.fixture
def empty_project_table():
    Project.objects.all().delete()


@pytest.mark.django_db
def test_load_project_data(empty_project_table):
    # Ensure the database is empty before running the command
    assert Project.objects.count() == 0

    # Call the management command
    call_command("load_project_data")

    # Verify that the projects have been loaded correctly
    for project_data in PROJECTS_DATA:
        project = Project.objects.get(year=project_data["year"])
        assert project.year == project_data["year"]
        for lang_code, name in project_data["translations"].items():
            project.set_current_language(lang_code)
            assert project.name == name

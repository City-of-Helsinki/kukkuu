import pytest
from django.contrib.admin.sites import AdminSite
from django.utils.translation import gettext_lazy as _

from events.admin import EventGroupAdmin, EventGroupForm
from events.factories import EventFactory, EventGroupFactory
from kukkuu.consts import DATA_VALIDATION_ERROR
from projects.factories import ProjectFactory


class MockRequest:
    pass


@pytest.mark.django_db
def test_event_group_form_valid_when_events_in_same_project():
    project = ProjectFactory(year=3000)
    event1 = EventFactory(project=project)
    event2 = EventFactory(project=project)

    form_data = {
        "project": project.id,
        "name_fi": "Testiryhmä",
        "events": [event1.id, event2.id],
    }
    form = EventGroupForm(data=form_data)
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_event_group_form_invalid_when_events_in_different_project():
    project1 = ProjectFactory(year=3001)
    project2 = ProjectFactory(year=3002)
    event1 = EventFactory(project=project1)
    event2 = EventFactory(project=project2)

    form_data = {
        "project": project1.id,
        "name_fi": "Testiryhmä",
        "events": [event1.id, event2.id],
    }
    form = EventGroupForm(data=form_data)
    assert not form.is_valid()
    assert "events" in form.errors
    expected_error = _(
        "The event group and its events must belong to the same project."
    )
    assert expected_error in form.errors["events"]
    assert any(
        error.code == DATA_VALIDATION_ERROR for error in form.errors.as_data()["events"]
    )


@pytest.mark.django_db
def test_event_group_form_valid_without_events():
    project = ProjectFactory(year=3003)
    form_data = {
        "project": project.id,
        "name_fi": "Testiryhmä",
        "events": [],
    }
    form = EventGroupForm(data=form_data)
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_event_group_form_update_mismatched_project():
    project1 = ProjectFactory(year=3004)
    project2 = ProjectFactory(year=3005)
    event_group = EventGroupFactory(project=project1)
    event = EventFactory(project=project1, event_group=event_group)

    # Change the project to project2 while keeping event from project1
    form_data = {
        "project": project2.id,
        "name_fi": "Päivitetty ryhmä",
        "events": [event.id],
    }
    form = EventGroupForm(data=form_data, instance=event_group)
    assert not form.is_valid()
    assert "events" in form.errors
    expected_error = _(
        "The event group and its events must belong to the same project."
    )
    assert expected_error in form.errors["events"]


@pytest.mark.django_db
def test_event_group_admin_save_model_flow():
    project = ProjectFactory(year=3006)
    event1 = EventFactory(project=project)
    event2 = EventFactory(project=project)

    form_data = {
        "project": project.id,
        "name_fi": "Admin ryhmä",
        "events": [event1.id, event2.id],
    }
    form = EventGroupForm(data=form_data)
    assert form.is_valid()

    admin = EventGroupAdmin(model=form.Meta.model, admin_site=AdminSite())
    obj = form.save(commit=False)
    admin.save_model(request=MockRequest(), obj=obj, form=form, change=False)

    assert obj.pk is not None
    assert set(obj.events.all()) == {event1, event2}

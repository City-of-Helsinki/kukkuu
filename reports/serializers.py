from datetime import date
from typing import Any, List, Optional

from django.utils.timezone import localdate
from drf_spectacular.utils import (
    extend_schema_field,
)
from rest_framework import serializers

from children.models import Child
from events.models import Event, EventGroup, Occurrence
from projects.models import Project
from reports.consts import (
    CONTACT_LANGUAGE_PRIORITIES,
    CONTACT_LANGUAGE_TO_LANGUAGE,
    LANGUAGE_CHOICES,
    OTHER_LANGUAGE_API_NAME,
)
from venues.models import Venue


def get_primary_contact_language(contact_languages: List[str]):
    return [
        contact_lang
        for lang in CONTACT_LANGUAGE_PRIORITIES
        for contact_lang in contact_languages
        if contact_lang == lang
    ][0]


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ChildSerializer(serializers.ModelSerializer):
    child_birthyear_postal_code_guardian_emails_hash = serializers.SerializerMethodField(  # noqa
        help_text="Salted hash of child's birthyear, postal code and guardians' emails."
    )
    child_name_birthyear_postal_code_guardian_emails_hash = (
        serializers.SerializerMethodField(
            help_text="Salted hash of child's name (i.e. first name and last name), "
            "birthyear, postal code and guardians' emails."
        )
    )
    registration_date = serializers.SerializerMethodField()
    birthyear = serializers.SerializerMethodField()
    contact_language = serializers.SerializerMethodField()
    languages_spoken_at_home = serializers.SerializerMethodField(
        help_text="Array of ISO 639-3 (language) or ISO 639-5 (language family) "
        "alpha-3 codes. Value `__OTHER__` means any other language."  # noqa
    )
    is_obsolete = serializers.SerializerMethodField(
        help_text="Are all the child's guardian user instances marked as obsolete?"
    )

    class Meta:
        model = Child
        fields = [
            "child_birthyear_postal_code_guardian_emails_hash",
            "child_name_birthyear_postal_code_guardian_emails_hash",
            "registration_date",
            "birthyear",
            "postal_code",
            "contact_language",
            "languages_spoken_at_home",
            "is_obsolete",
        ]

    def get_child_birthyear_postal_code_guardian_emails_hash(self, child: Child) -> str:
        """
        Salted hash of child's birthyear, postal code and guardians' emails.
        """
        return child.birthyear_postal_code_guardian_emails_hash

    def get_child_name_birthyear_postal_code_guardian_emails_hash(
        self, child: Child
    ) -> str:
        """
        Salted hash of child's name (i.e. first name and last name), birthyear, postal
        code and guardians' emails.
        """
        return child.name_birthyear_postal_code_guardian_emails_hash

    def get_registration_date(self, obj: Child) -> date:
        return localdate(obj.created_at)

    def get_birthyear(self, obj: Child) -> int:
        return obj.birthyear

    @extend_schema_field(
        serializers.ChoiceField(
            choices=(("fin", "Finnish"), ("swe", "Swedish"), ("eng", "English"))
        )
    )
    def get_contact_language(self, obj: Child) -> str:
        contact_languages = [
            guardian.language for guardian in list(obj.guardians.all())
        ]
        primary_contact_lang = get_primary_contact_language(contact_languages)
        return CONTACT_LANGUAGE_TO_LANGUAGE[primary_contact_lang]

    @extend_schema_field(
        serializers.ListField(child=serializers.ChoiceField(choices=LANGUAGE_CHOICES))
    )
    def get_languages_spoken_at_home(self, obj: Child) -> List[Optional[str]]:
        return [
            lang.alpha_3_code or OTHER_LANGUAGE_API_NAME
            for lang in obj.guardians.all()[0].prefetched_languages_spoken_at_home
        ]

    def get_is_obsolete(self, obj: Child) -> bool:
        return obj.is_obsolete


class ProjectSerializer(DynamicFieldsModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "year", "name"]

    # NOTE: Fetching the translations from django-parler table
    # can cause lots of sub queries.
    def get_name(self, obj: Project):
        return obj.name_with_translations


class VenueSerializer(
    DynamicFieldsModelSerializer, serializers.HyperlinkedModelSerializer
):
    name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    project = ProjectSerializer(
        # To optimize the query, exclude django-parler translated fields and
        # offer url for details instead
        fields=[
            "id",
            "year",
        ],
        read_only=True,
        help_text="A project describes the year group where "
        "the children can participate. A venue is a project specific object.",
    )

    class Meta:
        model = Venue
        fields = ["url", "id", "project", "name", "address"]

    # NOTE: Fetching the translations from django-parler table
    # can cause lots of sub queries.
    def get_name(self, obj: Venue):
        return obj.name_with_translations

    # NOTE: Fetching the translations from django-parler table
    # can cause lots of sub queries.
    def get_address(self, obj: Venue):
        return obj.address_with_translations


class OccurrenceSerializer(serializers.ModelSerializer):
    enrolment_count = serializers.SerializerMethodField(
        help_text="Count of how many children have enrolled "
        "in this occurrence of an event."
    )

    attended_count = serializers.SerializerMethodField(
        help_text="Count of how many children atteded in this occurrence of an event."
    )

    capacity = serializers.SerializerMethodField(
        help_text="The total capacity of how many children can there participate "
        "in this occurrence of an event."
    )

    venue = VenueSerializer(
        read_only=True,
        # To optimize the query, exclude django-parler translated fields and
        # offer url for details instead
        fields=[
            "url",
            "id",
        ],
    )

    class Meta:
        model = Occurrence
        fields = [
            "id",
            "time",
            "venue",
            "enrolment_count",
            "attended_count",
            "capacity",
        ]

    def get_enrolment_count(self, obj: Occurrence) -> int:
        return obj.get_enrolment_count()

    def get_attended_count(self, obj: Occurrence) -> int:
        return obj.get_attended_enrolment_count()

    def get_capacity(self, obj: Occurrence) -> Optional[int]:
        return obj.get_capacity()


class EventGroupSerializer(
    DynamicFieldsModelSerializer, serializers.HyperlinkedModelSerializer
):
    name = serializers.SerializerMethodField()
    project = ProjectSerializer(
        # To optimize the query, exclude django-parler translated fields and
        # offer url for details instead
        fields=[
            "id",
            "year",
        ],
        read_only=True,
        help_text="A project describes the year group where "
        "the children can participate.",
    )
    events_count = serializers.SerializerMethodField(
        help_text="Total count of events in this event group."
    )
    enrolment_count = serializers.SerializerMethodField(
        help_text="Total count of how many children have enrolled "
        "in this event group's event occurrences."
    )
    attended_count = serializers.SerializerMethodField(
        help_text="Count of how many children atteded "
        "in this event group's event occurrences."
    )
    capacity = serializers.SerializerMethodField(
        help_text="The total capacity of how many children can there participate "
        "in this event group's event occurrences."
    )

    class Meta:
        model = EventGroup
        fields = [
            "url",
            "id",
            "name",
            "project",
            "events_count",
            "enrolment_count",
            "attended_count",
            "capacity",
        ]

    def get_events_count(self, obj: EventGroup) -> int:
        return obj.events.count()

    def get_enrolment_count(self, obj: EventGroup) -> int:
        return obj.get_enrolment_count()

    def get_attended_count(self, obj: EventGroup) -> int:
        return obj.get_attended_enrolment_count()

    def get_capacity(self, obj: EventGroup) -> Optional[int]:
        return obj.get_capacity()

    # NOTE: Fetching the translations from django-parler table
    # can cause lots of sub queries.
    def get_name(self, obj: Project):
        return obj.name_with_translations


class EventSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    project = ProjectSerializer(
        # To optimize the query, exclude django-parler translated fields and
        # offer url for details instead
        fields=[
            "id",
            "year",
        ],
        read_only=True,
        help_text="A project describes the year group where "
        "the children can participate.",
    )
    event_group = EventGroupSerializer(
        # To optimize the query, exclude django-parler translated fields and
        # offer url for details instead
        fields=[
            "url",
            "id",
        ],
        read_only=True,
        help_text="The event can belong to an event group "
        "that contains a group of events.",
    )
    occurrences = OccurrenceSerializer(
        many=True,
        read_only=True,
        help_text="A single event can contain 1 or multiple occurrences "
        "that are held at different times",
    )
    occurrences_count = serializers.SerializerMethodField(
        help_text="Total count of occurrences in this event."
    )
    enrolment_count = serializers.SerializerMethodField(
        help_text="Total count of how many children have enrolled "
        "in this event's occurrences."
    )
    attended_count = serializers.SerializerMethodField(
        help_text="Count of how many children atteded in this event's occurrences."
    )
    capacity = serializers.SerializerMethodField(
        help_text="The total capacity of how many children can there participate "
        "in this event's occurrences."
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "project",
            "event_group",
            "occurrences",
            "ticket_system",
            "occurrences_count",
            "enrolment_count",
            "attended_count",
            "capacity",
        ]

    def get_occurrences_count(self, obj: Event) -> int:
        return obj.occurrences.count()

    def get_enrolment_count(self, obj: Event) -> int:
        return obj.get_enrolment_count()

    def get_attended_count(self, obj: Event) -> int:
        return obj.get_attended_enrolment_count()

    def get_capacity(self, obj: Event) -> Optional[int]:
        return obj.get_capacity()

    # NOTE: Fetching the translations from django-parler table
    # can cause lots of sub queries.
    def get_name(self, obj: Project) -> dict[Any, str]:
        return obj.name_with_translations

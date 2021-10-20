from django.core.management import BaseCommand
from django.db import transaction
from django.utils import translation

from languages.models import Language, LanguageAlreadyExistsError

DEFAULT_LANGUAGES_FILE = "data/default_languages.csv"


class Command(BaseCommand):
    help = "Adds languages and language families by their ISO 639-3 or ISO 639-5 alpha-3 codes."  # noqa: E501

    def add_arguments(self, parser):
        parser.add_argument(
            "codes",
            nargs="?",
            type=str,
            help="Comma-separated list of codes to be added.",
        )
        parser.add_argument(
            "--default",
            action="store_true",
            help=f'Add default languages provided in file "{DEFAULT_LANGUAGES_FILE}" and special language "Other".',  # noqa: E501
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Flush all existing languages before adding new ones. Use with caution!",  # noqa: E501
        )

    @transaction.atomic
    @translation.override("en")
    def handle(self, *args, **options):
        if not any(options[a] for a in ("flush", "default", "codes")):
            self.stdout.write("Nothing to do. Hint: try --help.")
            return

        if options["flush"]:
            Language.objects.all().delete()
            self.stdout.write("Flushed existing languages")

        codes = []

        if options["default"]:
            with open(DEFAULT_LANGUAGES_FILE, "rt") as f:
                codes.extend(f.read().split(","))

            try:
                Language.objects.create_option_other()
                self.stdout.write('Created special language "Other"')
            except LanguageAlreadyExistsError:
                self.stdout.write('Special language "Other" already exists')

        if options["codes"] is not None:
            codes.extend(options["codes"].split(","))

        for code in codes:
            code = code.strip()
            try:
                language = Language.objects.create_from_language_code(code)
                self.stdout.write(f"Created {language}")
            except LanguageAlreadyExistsError:
                language_str = (
                    Language.objects.filter(alpha_3_code=code).first() or code
                )
                self.stdout.write(f"{language_str} already exists")

        self.stdout.write(self.style.SUCCESS("All done!"))

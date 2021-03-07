import time
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.management import BaseCommand
from mailer.engine import send_all
from mailer.models import Message


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("num_of_threads", nargs="?", type=int)

        parser.add_argument(
            "--flush", action="store_true",
        )

        parser.add_argument(
            "--publish", action="store_true",
        )

    def handle(self, *args, **options):
        num_of_mails = Message.objects.non_deferred().count()
        num_of_threads = (
            options["num_of_threads"] or settings.KUKKUU_THREADED_SEND_MAIL_THREAD_COUNT
        )
        start_time = time.perf_counter()

        if num_of_mails < settings.KUKKUU_THREADED_SEND_MAIL_THRESHOLD:
            self.stdout.write(f"Sending mails...")
            send_all()
        else:
            self.stdout.write(f"Sending mails with {num_of_threads} threads...")

            with ThreadPoolExecutor(max_workers=num_of_threads) as executor:
                for _ in range(num_of_threads):
                    executor.submit(send_all)

        self.stdout.write(
            f"~{num_of_mails} mails sent in "
            f"{time.perf_counter() - start_time:0.2f} seconds."
        )

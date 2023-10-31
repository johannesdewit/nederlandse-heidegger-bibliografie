from tqdm import tqdm
import json

from django.core.management.base import BaseCommand
from django.conf import settings

from nederlandse_heidegger_bibliografie.models import BibEntry


class Command(BaseCommand):
    def _flush_table(self, Model):
        n, info = Model.objects.all().delete()
        if n:
            self.stdout.write(f"{n} objects deleted")
            for object_type, no_objects in info.items():
                self.stdout.write(f"- {object_type}: {no_objects}")

    def add_arguments(self, parser):
        # By default we perform external calls (Perseus, Citeproc, etc.) only in production (DEBUG == False),
        # not in development (DEBUG == True). Either -e or -n can be used to overwrite this behaviour.
        parser.add_argument(
            "--external-calls",
            "-e",
            action="store_true",
            help=f"Run with external calls (population script will be complete, but slower). Default: {not settings.DEBUG}",
        )
        parser.add_argument(
            "--no-external-calls",
            "-n",
            action="store_true",
            help=f"Run without external calls to speed up the populate script (but skip some fields). Default: {bool(settings.DEBUG)}",
        )

        return super().add_arguments(parser)

    def handle(self, *args, **kwargs):
        if kwargs.get("external_calls"):
            perform_external_calls = True
        elif kwargs.get("no_external_calls"):
            perform_external_calls = False
        else:
            perform_external_calls = not settings.DEBUG

        # Clean DB
        for Model in [BibEntry]:
            self._flush_table(Model)

        # Load bib data
        with open(settings.BIB_DATA) as f:
            bib_data = json.load(f)

        # Populate bib
        bib_objs = []
        for i in bib_data:
            bib_obj = BibEntry(id=i['id'], csl_data=i)

            bib_objs.append(bib_obj)

        BibEntry.objects.bulk_create(tqdm(bib_objs, desc="Populating bibliography"))
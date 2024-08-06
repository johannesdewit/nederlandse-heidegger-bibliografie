from requests import HTTPError
from tqdm import tqdm
from glob import glob
from pathlib import Path
import json
import frontmatter

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

        # Load citation data
        citation_data_by_id = {}
        for fpath in tqdm(
            glob(str(settings.CITATION_DATA_DIR / "*.md")), desc="Loading citation data"
        ):
            with open(fpath) as f:
                md_frontmatter = frontmatter.load(f)
                md_body = md_frontmatter.content

                citation_info = {}
                bib_id = md_frontmatter['citekey']
                
                try:
                    citation_info['indexed'] = md_frontmatter['geïndexeerd']
                except:
                    citation_info['indexed'] = False

                citation_list = []

                try: 
                    for l in md_body.splitlines():
                        ref = l.strip("[]@")
                        citation_list.append(ref)
                except:
                    continue

                citation_info['citations'] = citation_list

            citation_data_by_id[bib_id] = citation_info

        # Load bib data
        with open(settings.BIB_DATA, encoding='utf-8') as f:
            bib_data = json.load(f)

        # Populate bib
        bib_objs = []
        for i in tqdm(bib_data, desc="Parsing data (and generating references)"):
            bib_id = i['id']
            year_issued = i['issued']['date-parts'][0][0]
            
            try: 
                indexed = citation_data_by_id[bib_id]['indexed']
            except:
                indexed = False
            bib_obj = BibEntry(
                id=bib_id,
                csl_json=i,
                year_issued=year_issued,
                indexed=indexed
                )

            if perform_external_calls:
                try:
                    bib_obj.gen_reference()
                except HTTPError as e:
                    self.stdout.write(
                        f"Skipping {bib_id} reference generation because of HTTP error: {e}"
                    )
            else:
                bib_obj.reference = "—"

            bib_objs.append(bib_obj)

        BibEntry.objects.bulk_create(tqdm(bib_objs, desc="Populating bibliography"))

        # Populate citations
        for bib_obj in tqdm(BibEntry.objects.all(), desc="Adding citation relations"):
            bib_id = bib_obj.id

            if citation_data_by_id.get(bib_id):
                for i in citation_data_by_id[bib_id]['citations']:
                    try:
                        bib_obj.citations.add(BibEntry.objects.get(id=i))
                    except ValueError as e:
                        print(f"{bib_id}: {e}")
                    except:
                        print(f"Error: Cited work {i} not found")
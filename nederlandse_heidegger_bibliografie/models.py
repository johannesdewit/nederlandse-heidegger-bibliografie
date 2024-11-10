import requests
import datetime

from django.db import models
from django.conf import settings

class Author(models.Model):
    id = models.CharField(max_length=256, unique=True, primary_key=True)
    csl_json = models.JSONField()

    def __str__(self):
        return self.full_name

    @property
    def given_name(self) -> str:
        first_name = self.csl_json["given"]

        return first_name

    @property
    def family_name_affix(self) -> str:
        family_name_affix = None

        try:
            family_name_affix = self.csl_json["non-dropping-particle"]
        except KeyError:
            pass
        try:            
            family_name_affix = self.csl_json["dropping-particle"]
        except KeyError:
            pass

        return family_name_affix

    @property
    def family_name(self) -> str:
        family_name = self.csl_json["family"]

        return family_name

    @property
    def full_name(self) -> str:
        if self.family_name_affix:
            return f"{self.given_name} {self.family_name_affix} {self.family_name}"
        else:
            return f"{self.given_name} {self.family_name}"
        
    @property
    def first_letter(self):
        return self.family_name[0].upper()

    class Meta:
        ordering = ["id"]

class BibEntry(models.Model):
    # TODO Regex id to match BetterBibtex id's
    id = models.CharField(max_length=256, unique=True, primary_key=True)
    csl_json = models.JSONField()
    year_issued = models.PositiveSmallIntegerField(null=True)
    reference = models.TextField(max_length=1024, null=True)
    indexed = models.BooleanField(default=False)
    citations = models.ManyToManyField("self", symmetrical=False, related_name="cited_by")
    author = models.ManyToManyField(Author, related_name="works")
    # TODO: add url field and seperate URLs from the reference.

    def __str__(self):
        return self.id

    @property
    def first_letter(self):
        return self.id[0].upper()

    @property
    def title(self):
        return self.csl_json.get("title-short") or self.csl_json.get("title") or ""
    
    def gen_reference(self):
        if not self.reference and self.csl_json:
            r = requests.post(
                settings.CITEPROC_ENDPOINT,
                json={"items": [self.csl_json]},
                params={
                    "style": settings.CITEPROC_STYLE,
                    "responseformat": "html",
                    "locale": settings.LANGUAGE_CODE,
                    "linkwrap": 1
                },
            )
            r.raise_for_status()
            self.reference = r.content.decode()

    class Meta:
        ordering = ["id"]
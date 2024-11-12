import requests
import datetime

from django.db import models
from django.conf import settings

class Author(models.Model):
    id = models.CharField(max_length=256, unique=True, primary_key=True)
    csl_json = models.JSONField()
    family_name = models.CharField(max_length=64, blank=True)
    family_name_affix = models.CharField(max_length=16, blank=True, null=True)
    given_name = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.full_name

    @property
    def full_name(self) -> str:
        if self.family_name_affix:
            return f"{self.given_name} {self.family_name_affix} {self.family_name}"
        else:
            return f"{self.given_name} {self.family_name}"
        
    @property
    def first_letter(self) -> str:
        return self.family_name[0].upper()

    class Meta:
        ordering = ["family_name", "given_name"]
        verbose_name = "author"

class BibEntry(models.Model):
    # TODO Regex id to match BetterBibtex id's
    id = models.CharField(max_length=256, unique=True, primary_key=True)
    sort_key = models.SlugField(max_length=64, unique=True, null=True)
    csl_json = models.JSONField()
    year_issued = models.PositiveSmallIntegerField(null=True)
    reference = models.TextField(max_length=1024, null=True)
    indexed = models.BooleanField(default=False)
    citations = models.ManyToManyField("self", symmetrical=False, related_name="cited_by")
    author = models.ManyToManyField(Author, related_name="works")
    editor = models.ManyToManyField(Author, related_name="edited")
    title = models.CharField(max_length=256, null=True)
    # TODO: add url field and seperate URLs from the reference.

    def __str__(self):
        return self.id
    
    @property
    def first_letter(self):
        first_letter = self.sort_key[0].upper()
        return first_letter
    
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
        ordering = ["sort_key"]
        verbose_name = "bibliography entry"
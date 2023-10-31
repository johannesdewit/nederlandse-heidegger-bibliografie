import requests
from django.db import models
from django.conf import settings


class BibEntry(models.Model):
    # TODO Regex id to match BetterBibtex id's
    id = models.CharField(max_length=256, unique=True, primary_key=True)
    csl_json = models.JSONField()
    reference = models.TextField(max_length=1024, null=True)
    indexed = models.BooleanField(default=False)

    def __str__(self):
        return self.id
    
    def gen_reference(self):
        if not self.reference and self.csl_json:
            r = requests.post(
                settings.CITEPROC_ENDPOINT,
                json={"items": [self.csl_json]},
                params={"style": settings.CITEPROC_STYLE, "responseformat": "html", "locale": "nl-NL"},
            )
            r.raise_for_status()
            self.reference = r.content.decode()
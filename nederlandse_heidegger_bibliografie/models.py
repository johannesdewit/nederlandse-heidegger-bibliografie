from django.db import models

class BibEntry(models.Model):
    id = models.CharField(max_length=256, unique=True, primary_key=True)
    csl_data = models.JSONField()
    ref = models.TextField(max_length=1024, null=True)
    indexed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
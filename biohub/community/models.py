from django.db import models

from biohub.accounts.models import User
from biohub.editor.models import Report


class Star(models.Model):
    starrer = models.ForeignKey(User)
    starred_report = models.ForeignKey(Report)
    created = models.DateTimeField(auto_now_add=True)


class Collection(models.Model):
    name = models.CharField(max_length=125)
    collector = models.ForeignKey(User)
    reports = models.ManyToManyField(Report, null=True)


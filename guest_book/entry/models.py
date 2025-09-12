from django.db import models

from libs.models.abstract import TimestampedModel


class Entry(TimestampedModel):
    user = models.ForeignKey("user.User", related_name="entries", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()

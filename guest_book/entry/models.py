from django.db import models

from libs.models.abstract import TimestampedModel


class Entry(TimestampedModel):
    user = models.ForeignKey("user.User", related_name="entries", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()

    class Meta:
        indexes = [models.Index(fields=["user", "-created_date"], name="idx_entry_user_date_desc")]

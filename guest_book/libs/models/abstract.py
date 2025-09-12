from django.db import models


class TimestampedModel(models.Model):
    """Abstract model which adds creation and update timestamps"""

    class Meta:
        abstract = True

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_date = models.DateTimeField(auto_now=True)

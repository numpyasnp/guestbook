from django.db import models

from libs.models.abstract import TimestampedModel


class User(TimestampedModel):
    name = models.CharField(
        max_length=255, unique=True, help_text="Unique name of the guest"  # unique true already indexed from django
    )

    class Meta:
        db_table = "user"

    def __str__(self):
        return f"{self.name}"

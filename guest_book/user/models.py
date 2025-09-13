from django.db import models
from django.db.models import QuerySet, Value, CharField, OuterRef, Count, Subquery
from django.db.models.functions import Concat

from entry.models import Entry
from libs.models.abstract import TimestampedModel


class UserQuerySet(QuerySet):
    def with_entry_summary(self):
        """Annotates users with their total entry count and the last entry's subject and message."""
        latest_entry_subquery = (
            Entry.objects.filter(user_id=OuterRef("pk"))
            .order_by("-created_date")
            .annotate(subject_message=Concat("subject", Value(" | "), "message", output_field=CharField()))
            .values("subject_message")[:1]
        )

        return self.annotate(total_entries=Count("entries"), last_entry=Subquery(latest_entry_subquery))


class User(TimestampedModel):
    name = models.CharField(
        max_length=255, unique=True, help_text="Unique name of the guest"  # unique true already indexed from django
    )

    objects = UserQuerySet.as_manager()

    class Meta:
        db_table = "user"

    def __str__(self):
        return f"{self.name}"

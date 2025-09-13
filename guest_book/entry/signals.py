from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from entry.models import Entry

CACHE_KEY_COUNT = "entry_count"


@receiver(post_save, sender=Entry)
@receiver(post_delete, sender=Entry)
def invalidate_guestbook_count_cache(sender, **kwargs):
    cache.delete(CACHE_KEY_COUNT)

# Optional cache invalidation:
# If count accuracy is important and entries do not change frequently,
# this signal handler can be activated to invalidate the cached count.

# CACHE_KEY_COUNT = "entry_count"
#
#
# @receiver(post_save, sender=Entry)
# @receiver(post_delete, sender=Entry)
# def invalidate_entry_count_cache(sender, **kwargs):
#     cache.delete(CACHE_KEY_COUNT)

# NOTE

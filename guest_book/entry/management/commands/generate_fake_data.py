from django.core.management.base import BaseCommand

from libs.normalize import turkish_str
from user.models import User
from entry.models import Entry
from faker import Faker
import random


class Command(BaseCommand):
    help = "Generate fake Users and Entries with bulk_create"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=1000, help="Number of users to create")
        parser.add_argument("--entries", type=int, default=10000, help="Number of entries to create")
        parser.add_argument("--batch", type=int, default=1000, help="Batch size for bulk_create")

    def handle(self, *args, **options):
        fake = Faker()

        users_count = options["users"]
        entries_count = options["entries"]
        batch_size = options["batch"]

        self.stdout.write(self.style.WARNING(f"Creating {users_count} users..."))

        users = [User(name=turkish_str(fake.unique.name()).capitalize()) for _ in range(users_count)]
        User.objects.bulk_create(users, batch_size=batch_size)

        self.stdout.write(self.style.SUCCESS(f"{users_count} users created."))

        all_users = list(User.objects.all())
        self.stdout.write(self.style.WARNING(f"Creating {entries_count} entries..."))

        entries = []
        for i in range(entries_count):
            entries.append(
                Entry(
                    user=random.choice(all_users),
                    subject=fake.sentence(nb_words=6),
                    message=fake.paragraph(nb_sentences=5),
                )
            )
            if len(entries) >= batch_size:
                Entry.objects.bulk_create(entries, batch_size=batch_size)
                entries = []

        if entries:
            Entry.objects.bulk_create(entries, batch_size=batch_size)

        self.stdout.write(self.style.SUCCESS(f"{entries_count} entries created."))

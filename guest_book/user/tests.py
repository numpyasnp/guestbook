from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status

from entry.models import Entry
from user.models import User


class TestUserAPI(TestCase):

    def setUp(self):
        self.client = APIClient()
        cache.clear()

    def test_get_users_empty_list(self):
        # When
        response = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["users"]), 0)

    def test_get_users_with_entries(self):
        # Given
        user1 = User.objects.create(name="John Doe")
        user2 = User.objects.create(name="Jane Smith")

        Entry.objects.create(user=user1, subject="First Entry", message="First message")
        Entry.objects.create(user=user1, subject="Second Entry", message="Second message")
        Entry.objects.create(user=user2, subject="Only Entry", message="Only message")

        # When
        response = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["users"]), 2)

        # Check user data structure
        for user_data in data["users"]:
            self.assertIn("username", user_data)
            self.assertIn("total_entries", user_data)
            self.assertIn("last_entry", user_data)

    def test_get_users_total_entries_count(self):
        # Given
        user = User.objects.create(name="Test User")
        Entry.objects.create(user=user, subject="Entry 1", message="Message 1")
        Entry.objects.create(user=user, subject="Entry 2", message="Message 2")
        Entry.objects.create(user=user, subject="Entry 3", message="Message 3")

        # When
        response = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        user_data = data["users"][0]
        self.assertEqual(user_data["total_entries"], 3)

    def test_get_users_last_entry_format(self):
        # Given
        user = User.objects.create(name="Test User")
        Entry.objects.create(user=user, subject="First Subject", message="First Message")
        Entry.objects.create(user=user, subject="Latest Subject", message="Latest Message")

        # When
        response = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        user_data = data["users"][0]
        self.assertEqual(user_data["last_entry"], "Latest Subject | Latest Message")

    def test_get_users_multiple_entries_last_one(self):
        # Given
        user = User.objects.create(name="Test User")
        Entry.objects.create(user=user, subject="First Subject", message="First Message")
        Entry.objects.create(user=user, subject="Second Subject", message="Second Message")
        Entry.objects.create(user=user, subject="Last Subject", message="Last Message")

        # When
        response = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        user_data = data["users"][0]
        self.assertEqual(user_data["last_entry"], "Last Subject | Last Message")

    def test_get_users_without_entries(self):
        # Given
        User.objects.create(name="User Without Entries")

        # When
        response = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        user_data = data["users"][0]
        self.assertEqual(user_data["total_entries"], 0)
        self.assertIsNone(user_data["last_entry"])

    def test_get_users_cache_functionality(self):
        # Given
        user = User.objects.create(name="Test User")
        Entry.objects.create(user=user, subject="Test Subject", message="Test Message")

        # When - First request
        response1 = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # When - Second request (should be cached)
        response2 = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.json(), response2.json())

    def test_get_users_response_structure(self):
        # Given
        user = User.objects.create(name="John Doe")
        Entry.objects.create(user=user, subject="Test Subject", message="Test Message")

        # When
        response = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data["users"]), 1)

        user_data = data["users"][0]
        expected_keys = {"username", "total_entries", "last_entry"}
        self.assertEqual(set(user_data.keys()), expected_keys)

    def test_get_users_with_special_characters(self):
        # Given
        user = User.objects.create(name="User 🎉")
        Entry.objects.create(
            user=user, subject="Special Subject: @#$%", message="Special Message: &*()_+-=[]{}|;':\",./<>?`~"
        )

        # When
        response = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        user_data = data["users"][0]
        self.assertEqual(user_data["username"], "User 🎉")
        self.assertIn("Special Subject: @#$%", user_data["last_entry"])
        self.assertIn("Special Message: &*()_+-=[]{}|;':\",./<>?`~", user_data["last_entry"])

    def test_get_users_long_messages(self):
        # Given
        user = User.objects.create(name="Test User")
        long_subject = "x" * 200
        long_message = "y" * 1000
        Entry.objects.create(user=user, subject=long_subject, message=long_message)

        # When
        response = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        user_data = data["users"][0]
        self.assertEqual(user_data["last_entry"], f"{long_subject} | {long_message}")

    def test_get_users_multiple_users_different_entry_counts(self):
        # Given
        user1 = User.objects.create(name="Active User")
        user2 = User.objects.create(name="Inactive User")

        # User1 has 3 entries
        for i in range(3):
            Entry.objects.create(user=user1, subject=f"Entry {i+1}", message=f"Message {i+1}")

        # User2 has 1 entry
        Entry.objects.create(user=user2, subject="Single Entry", message="Single Message")

        # When
        response = self.client.get(reverse("api:v1:user:list-users"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Find users by name
        active_user = next(user for user in data["users"] if user["username"] == "Active User")
        inactive_user = next(user for user in data["users"] if user["username"] == "Inactive User")

        self.assertEqual(active_user["total_entries"], 3)
        self.assertEqual(inactive_user["total_entries"], 1)
        self.assertEqual(active_user["last_entry"], "Entry 3 | Message 3")
        self.assertEqual(inactive_user["last_entry"], "Single Entry | Single Message")


class TestUserModel(TestCase):
    def test_user_with_entry_summary(self):
        # Given
        user = User.objects.create(name="Test User")
        Entry.objects.create(user=user, subject="user first subject", message="user first message")
        Entry.objects.create(user=user, subject="user last subject", message="user last message")

        # When
        users_with_summary = User.objects.with_entry_summary()

        # Then
        user_with_summary = users_with_summary.first()
        self.assertEqual(user_with_summary.total_entries, 2)
        self.assertEqual(user_with_summary.last_entry, "user last subject | user last message")

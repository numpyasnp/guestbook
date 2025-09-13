from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from entry.models import Entry
from user.models import User


class TestEntryAPI(TestCase):

    def setUp(self):
        self.client = APIClient()
        cache.clear()

    def test_create_entry_with_new_user(self):
        # Given
        payload = {
            "name": "John Doe",
            "subject": "Amazing experience",
            "message": "This site is really great. Thank you!",
        }

        # When
        response = self.client.post(reverse("api:v1:entry:entry-list-create"), data=payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(name="John Doe").exists())
        self.assertTrue(Entry.objects.filter(subject="Amazing experience").exists())

        data = response.json()
        self.assertEqual(data["subject"], "Amazing experience")
        self.assertEqual(data["message"], "This site is really great. Thank you!")

    def test_create_entry_with_existing_user(self):
        # Given
        user = User.objects.create(name="Jane Smith")
        payload = {"name": "Jane Smith", "subject": "Second message", "message": "This is my second entry"}

        # When
        response = self.client.post(reverse("api:v1:entry:entry-list-create"), data=payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(name="Jane Smith").count(), 1)
        self.assertTrue(Entry.objects.filter(user=user, subject="Second message").exists())

    def test_create_entry_validation_errors(self):
        # Given & When
        response = self.client.post(reverse("api:v1:entry:entry-list-create"), data={}, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Given
        payload = {"name": "Test User"}

        # When
        response = self.client.post(reverse("api:v1:entry:entry-list-create"), data=payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn("subject", response_data)
        self.assertIn("message", response_data)

        # Given
        payload = {"name": "Test User", "subject": "x" * 256, "message": "Test message"}

        # When
        response = self.client.post(reverse("api:v1:entry:entry-list-create"), data=payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_entries_empty(self):
        # When
        response = self.client.get(reverse("api:v1:entry:entry-list-create"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["page_size"], 3)
        self.assertEqual(data["total_pages"], 0)
        self.assertEqual(data["current_page_number"], 1)
        self.assertEqual(data["entries"], [])
        self.assertIsNone(data["links"]["next"])
        self.assertIsNone(data["links"]["previous"])

    def test_list_entries_with_pagination(self):
        # Given
        user = User.objects.create(name="Test User")
        for i in range(5):
            Entry.objects.create(user=user, subject=f"Subject {i+1}", message=f"Message {i+1}")

        # When
        response = self.client.get(reverse("api:v1:entry:entry-list-create"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 5)
        self.assertEqual(data["page_size"], 3)
        self.assertEqual(data["total_pages"], 2)
        self.assertEqual(data["current_page_number"], 1)
        self.assertEqual(len(data["entries"]), 3)
        self.assertIsNotNone(data["links"]["next"])
        self.assertIsNone(data["links"]["previous"])

        # When - Second Page
        response = self.client.get(f"{reverse('api:v1:entry:entry-list-create')}?page=2")

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["current_page_number"], 2)
        self.assertEqual(len(data["entries"]), 2)
        self.assertIsNone(data["links"]["next"])
        self.assertIsNotNone(data["links"]["previous"])

    def test_list_entries_ordering(self):
        # Given
        user = User.objects.create(name="Test User")
        Entry.objects.create(user=user, subject="First", message="First message")
        Entry.objects.create(user=user, subject="Second", message="Second message")
        Entry.objects.create(user=user, subject="Third", message="Third message")

        # When
        response = self.client.get(reverse("api:v1:entry:entry-list-create"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        entries = data["entries"]
        self.assertEqual(entries[0]["subject"], "Third")
        self.assertEqual(entries[1]["subject"], "Second")
        self.assertEqual(entries[2]["subject"], "First")

    def test_list_entries_response_format(self):
        # Given
        user = User.objects.create(name="Test User")
        Entry.objects.create(user=user, subject="Test Subject", message="Test Message")

        # When
        response = self.client.get(reverse("api:v1:entry:entry-list-create"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        entry = data["entries"][0]
        self.assertIn("user", entry)
        self.assertIn("subject", entry)
        self.assertIn("message", entry)
        self.assertIn("created_date", entry)
        self.assertEqual(entry["user"], "Test User")
        self.assertEqual(entry["subject"], "Test Subject")
        self.assertEqual(entry["message"], "Test Message")

    def test_pagination_cache(self):
        # Given
        user = User.objects.create(name="Test User")
        Entry.objects.create(user=user, subject="Test", message="Test")

        # When & Then - First request should write to cache
        with patch("api.v1.entry.pagination.cache.get", return_value=None) as mock_get:
            with patch("api.v1.entry.pagination.cache.set") as mock_set:
                response = self.client.get(reverse("api:v1:entry:entry-list-create"))
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                mock_set.assert_called_once()

        # When & Then - Second request should read from cache
        with patch("api.v1.entry.pagination.cache.get", return_value=1) as mock_get:
            response = self.client.get(reverse("api:v1:entry:entry-list-create"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_get.assert_called_once()

    def test_multiple_users_entries(self):
        # Given
        user1 = User.objects.create(name="User One")
        user2 = User.objects.create(name="User Two")
        Entry.objects.create(user=user1, subject="User One Subject", message="User One Message")
        Entry.objects.create(user=user2, subject="User Two Subject", message="User Two Message")

        # When
        response = self.client.get(reverse("api:v1:entry:entry-list-create"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["entries"]), 2)
        users = [entry["user"] for entry in data["entries"]]
        self.assertIn("User One", users)
        self.assertIn("User Two", users)

    def test_entry_character_limits(self):
        # Given
        payload = {"name": "Test User", "subject": "x" * 255, "message": "Test message"}

        # When
        response = self.client.post(reverse("api:v1:entry:entry-list-create"), data=payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Given
        payload = {"name": "Test User Two", "subject": "Long message test", "message": "x" * 10000}

        # When
        response = self.client.post(reverse("api:v1:entry:entry-list-create"), data=payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_entry_with_special_characters(self):
        # Given
        payload = {
            "name": "Test User 🎉",
            "subject": "Special characters: @#$%^&*()_+-=[]{}|;':\",./<>?`~",
            "message": "This message contains special characters and symbols!",
        }

        # When
        response = self.client.post(reverse("api:v1:entry:entry-list-create"), data=payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        entry = Entry.objects.get(subject="Special characters: @#$%^&*()_+-=[]{}|;':\",./<>?`~")
        self.assertEqual(entry.user.name, "Test User 🎉")
        self.assertIn("special characters", entry.message)

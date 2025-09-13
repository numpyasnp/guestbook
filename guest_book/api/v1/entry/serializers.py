from rest_framework import serializers

from entry.models import Entry
from user.models import User


class EntryCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)

    class Meta:
        model = Entry
        fields = ["name", "subject", "message"]

    def create(self, validated_data):
        name = validated_data.pop("name")
        user, _ = User.objects.get_or_create(name=name)
        entry = Entry.objects.create(user=user, **validated_data)
        return entry


class EntryResponseSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.name")

    class Meta:
        model = Entry
        fields = ["user", "subject", "message", "created_date"]

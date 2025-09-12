from rest_framework import serializers

from entry.models import Entry
from user.models import User


class EntrySerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)

    class Meta:
        model = Entry
        fields = ["username", "subject", "message"]

    def create(self, validated_data):
        username = validated_data.pop("username")
        user, _ = User.objects.get_or_create(name=username)
        entry = Entry.objects.create(user=user, **validated_data)
        return entry

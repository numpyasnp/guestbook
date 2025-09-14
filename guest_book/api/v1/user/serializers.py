from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(source="name")
    total_entries = serializers.IntegerField()
    last_entry = serializers.CharField()

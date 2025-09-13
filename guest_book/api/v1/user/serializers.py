from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    name = serializers.CharField()
    total_entries = serializers.IntegerField()
    last_entry = serializers.CharField()

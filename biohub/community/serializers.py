from rest_framework import serializers


class StarRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()

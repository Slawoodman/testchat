from chat.models import Message, Thread
from rest_framework import serializers
from django.contrib.auth.models import User


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source="sender.username")

    class Meta:
        model = Message
        fields = ("sender", "thread", "text", "created", "is_read")
        read_only_fields = ("created", "is_read")

    def create(self, validated_data):
        validated_data["sender"] = self.context["request"].user
        message = Message.objects.create(**validated_data)
        return message


class ThreadSerializer(serializers.ModelSerializer):
    participants = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all(), many=True
    )

    class Meta:
        model = Thread
        fields = ("participants",)
        read_only_fields = ("created", "updated")


class ReadMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("is_read",)

from rest_framework import serializers
from .models import ChatRoom, Message

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ["id", "participant_a", "participant_b", "created_at"]
        read_only_fields = ["id", "created_at"]

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "room", "sender_id", "content", "timestamp", "is_read"]
        read_only_fields = ["id", "timestamp"]

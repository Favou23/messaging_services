from django.shortcuts import render


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatRoom
from .serializers import ChatRoomSerializer, MessageSerializer
from django.shortcuts import get_object_or_404

class CreateOrGetRoom(APIView):
    def post(self, request):
        a = request.data.get("participant_a")
        b = request.data.get("participant_b")
        if not a or not b:
            return Response({"detail": "participant_a and participant_b required"}, status=status.HTTP_400_BAD_REQUEST)
        a_str, b_str = (a, b) if a < b else (b, a)
        room, created = ChatRoom.objects.get_or_create(participant_a=a_str, participant_b=b_str)
        serializer = ChatRoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class RoomMessages(APIView):
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        qs = room.messages.all()
        serializer = MessageSerializer(qs, many=True)
        return Response(serializer.data)

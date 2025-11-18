from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from .models import ChatRoom
from .auth_client import fetch_profile_sync
import logging
import httpx
from django.shortcuts import get_object_or_404
from chat.serializers import MessageSerializer

logger = logging.getLogger(__name__)

class CreateRoomSerializer(serializers.Serializer):
    participant_a = serializers.CharField(max_length=255, required=True, help_text="User ID of first participant")
    participant_b = serializers.CharField(max_length=255, required=True, help_text="User ID of second participant")

class CreateOrGetRoom(APIView):
    serializer_class = CreateRoomSerializer
    
    def post(self, request):
        # Validate input using serializer
        serializer = CreateRoomSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        participant_a = serializer.validated_data['participant_a']
        participant_b = serializer.validated_data['participant_b']
        
        # just added this line 
        print(f"✅ Participants validated: {participant_a}, {participant_b}")
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip() if auth_header.startswith('Bearer ') else None
        
        if not token:
            # just added this too
            print("❌ No token")
            return Response(
                {"detail": "Authentication required. Please provide a Bearer token."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Validate the requesting user exists
        logger.info(f"Validating token for user...")
        current_user = fetch_profile_sync(token)
        
        if not current_user:
            # added this too
            print("fetch_profile_sync returned None!")
            return Response(
                {"detail": "Invalid token or user not found in auth service"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        # added this too
        print(f"Profile fetched: {current_user}")
        
        current_user_id = str(current_user.get('id') or current_user.get('user_id'))
        print(f"User ID: {current_user_id}")
        
        # Verify current user is one of the participants
        if current_user_id not in [participant_a, participant_b]:
            # added this too
            print(f" User {current_user_id} not in participants")
            return Response(
                {"detail": "You can only create rooms where you are a participant"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        # added this too 
        print(f"User is participant")
        # added this too
        print(f"Verifying users exist...")
        
        
        # Verify both users exist in auth service
        # logger.info(f"Verifying users {participant_a} and {participant_b} exist...")
        users_valid = self.verify_users_exist([participant_a, participant_b], token)
        
        if not users_valid:
            print("❌ verify_users_exist returned False")
            return Response(
                {"detail": "One or more participants not found in auth service"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        print(f"✅ Users verified")
        # Normalize participant order (prevent duplicate rooms)
        if participant_a > participant_b:
            participant_a, participant_b = participant_b, participant_a
        
        # Create or get room
        try:
            room, created = ChatRoom.objects.get_or_create(
                participant_a=participant_a,
                participant_b=participant_b
            )
            
            logger.info(f"Room {'created' if created else 'retrieved'}: {room.id}")
            
            return Response({
                "room_id": room.id,
                "created": created,
                "participant_a": participant_a,
                "participant_b": participant_b,
                "created_at": room.created_at
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error creating/getting room: {str(e)}")
            return Response(
                {"detail": f"Database error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def verify_users_exist(self, user_ids, token):
        """Verify all users exist in auth service"""
        from django.conf import settings

        auth_url = getattr(settings, 'AUTH_API_URL', 'http://authservice:8080')

        for user_id in user_ids:
            try:
                # Try to fetch user profile from auth service
                url = f"{auth_url.rstrip('/')}/api/users/{user_id}/"
                headers = {"Authorization": f"Bearer {token}"}
                
                response = httpx.get(url, headers=headers, timeout=5.0)
                
                if response.status_code == 404:
                    logger.error(f"User {user_id} not found in auth service")
                    return False
                elif response.status_code != 200:
                    logger.warning(f"Auth service returned status {response.status_code} for user {user_id}")
                    # Continue anyway - might be auth service issue
                    
            except Exception as e:
                logger.error(f"Error verifying user {user_id}: {str(e)}")
                # Don't block room creation due to transient network issues
                
        return True
class RoomMessages (APIView):
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        qs = room.messages.all()
        serializer = MessageSerializer(qs, many=True)
        return Response(serializer.data)


# # messaging_services/chat/views.py

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, serializers
# from django.shortcuts import get_object_or_404
# import logging

# from .models import ChatRoom, Message
# from .serializers import MessageSerializer

# logger = logging.getLogger(__name__)


# class CreateRoomSerializer(serializers.Serializer):
#     participant_a = serializers.CharField(max_length=255, required=True)
#     participant_b = serializers.CharField(max_length=255, required=True)


# class CreateOrGetRoom(APIView):
#     """
#     Create or get a chat room between two participants.
    
#     TEMPORARY: Auth validation disabled for testing.
#     """
#     serializer_class = CreateRoomSerializer
    
#     def post(self, request):
#         print("\n" + "="*70)
#         print("🚀 CREATE ROOM REQUEST")
#         print("="*70)
        
#         # Validate input
#         serializer = CreateRoomSerializer(data=request.data)
#         if not serializer.is_valid():
#             print(f"❌ Validation failed: {serializer.errors}")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         participant_a = serializer.validated_data['participant_a']
#         participant_b = serializer.validated_data['participant_b']
#         print(f"✅ Participants: {participant_a} and {participant_b}")
        
#         # TODO: Add auth validation later
#         # For now, just create the room
#         print("⚠️  Auth validation SKIPPED (temporary)")
        
#         # Normalize participant order (prevent duplicates)
#         if participant_a > participant_b:
#             participant_a, participant_b = participant_b, participant_a
#             print(f"🔄 Normalized order: {participant_a}, {participant_b}")
        
#         # Create or get room
#         try:
#             room, created = ChatRoom.objects.get_or_create(
#                 participant_a=participant_a,
#                 participant_b=participant_b
#             )
            
#             print(f"{'✅ Room CREATED' if created else '✅ Room FOUND'}: ID={room.id}")
#             print("="*70 + "\n")
            
#             return Response({
#                 "success": True,
#                 "room_id": room.id,
#                 "created": created,
#                 "participant_a": participant_a,
#                 "participant_b": participant_b,
#                 "created_at": room.created_at,
#                 "message": "Room created successfully" if created else "Room already exists"
#             }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
#         except Exception as e:
#             print(f"❌ Database error: {e}")
#             print("="*70 + "\n")
#             logger.error(f"Error creating room: {str(e)}")
#             import traceback
#             traceback.print_exc()
            
#             return Response({
#                 "success": False,
#                 "detail": f"Database error: {str(e)}"
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class RoomMessages(APIView):
#     """Get all messages in a room"""
    
#     def get(self, request, room_id):
#         print(f"\n📨 Fetching messages for room {room_id}")
        
#         room = get_object_or_404(ChatRoom, id=room_id)
#         messages = room.messages.all()
#         serializer = MessageSerializer(messages, many=True)
        
#         print(f"✅ Found {messages.count()} messages\n")
#         return Response(serializer.data)
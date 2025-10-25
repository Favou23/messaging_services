import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from .models import ChatRoom, Message
from .auth_client import fetch_profile_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group = f"chat_{self.room_id}"
        
        self.user_id= None
        
        auth_user = self.scope.get("auth_user")
        if not auth_user:
            await self.close()
            return
        self.user_id = str(auth_user["user_id"])
        # verify membership
        allowed = await self._user_in_room(self.room_id, self.user_id)
        if not allowed:
            await self.close()
            return
        # Join room group
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        # announce presence in room (others can show online)
        await self.channel_layer.group_send(self.room_group, {
            "type":"presence.update",
            "user_id": self.user_id,
            "status": "online",
        })

    async def disconnect(self, code):
        # leave
        await self.channel_layer.group_discard(self.room_group, self.channel_name)
        if self.user_id:
            await self.channel_layer.group_send(self.room_group,{
                'type':"presence.update",
                'user_id':self.user_id,
                'status':'offline',
            })

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        data = json.loads(text_data)
        typ = data.get("type")
        if typ == "message":
            content = data.get("content", "").strip()
            if not content:
                return
            msg = await self._create_message(self.room_id, self.user_id, content)
            payload = {
                "type":"chat.message",
                "message": {
                    "id": msg.id,
                    "room": msg.room_id,
                    "sender_id": msg.sender_id,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
            }
            await self.channel_layer.group_send(self.room_group, payload)
        elif typ == "typing":
            is_typing = bool(data.get("is_typing"))
            await self.channel_layer.group_send(self.room_group, {
                "type": "typing.event",
                "user_id": self.user_id,
                "is_typing": is_typing,
            })
        elif typ == "fetch_profile":
            # optional: return profile for this user from Auth service
            token = self.scope.get("auth_user", {}).get("token")
            profile = None
            if token:
                profile = await fetch_profile_async(token)
            await self.send_json({"type":"profile", "profile": profile})
        else:
            # unknown type -> ignore or send error
            await self.send_json({"type":"error","detail":"unknown type"})

    # group handlers
    async def chat_message(self, event):
        await self.send_json(event["message"])

    async def typing_event(self, event):
        await self.send_json({
            "type": "typing",
            "user_id": event["user_id"],
            "is_typing": event["is_typing"],
        })

    async def presence_update(self, event):
        await self.send_json({
            "type": "presence",
            "user_id": event.get("user_id"),
            "status": event.get("status"),
        })

    # helpers
    @database_sync_to_async
    def _user_in_room(self, room_id, user_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            return user_id in (room.participant_a, room.participant_b)
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def _create_message(self, room_id, sender_id, content):
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(room=room, sender_id=sender_id, content=content)

class PresenceConsumer(AsyncWebsocketConsumer):
    """
    Optional consumer clients can subscribe to global presence channel.
    Send/receive presence updates here.
    """
    async def connect(self):
        await self.channel_layer.group_add("presence_global", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard("presence_global", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # this is optional: allow client to announce presence changes
        data = json.loads(text_data or "{}")
        action = data.get("action")
        if action == "status":
            user_id = data.get("user_id")
            status = data.get("status")
            if user_id and status:
                await self.channel_layer.group_send("presence_global", {
                    "type": "presence.broadcast",
                    "user_id": user_id,
                    "status": status,
                })

    async def presence_broadcast(self, event):
        await self.send_json({
            "type": "presence_global",
            "user_id": event.get("user_id"),
            "status": event.get("status"),
        })

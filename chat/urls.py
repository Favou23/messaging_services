from django.urls import path
from .views import CreateOrGetRoom, RoomMessages

urlpatterns = [
    path("rooms/", CreateOrGetRoom.as_view(), name="create_room"),
    path("rooms/<int:room_id>/messages/", RoomMessages.as_view(), name="room_messages"),
]

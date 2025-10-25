
from django.test import TestCase
from .models import ChatRoom

class ChatModelsTest(TestCase):
    def test_create_room(self):
        r = ChatRoom.objects.create(participant_a="1", participant_b="2")
        self.assertEqual(str(r), "1<->2")

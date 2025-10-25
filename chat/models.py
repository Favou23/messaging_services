
from django.db import models

class ChatRoom(models.Model):
    participant_a = models.CharField(max_length=255)
    participant_b = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("participant_a", "participant_b"),)

    def __str__(self):
        return f"{self.participant_a}<->{self.participant_b}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name="messages", on_delete=models.CASCADE)
    sender_id = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ("timestamp",)


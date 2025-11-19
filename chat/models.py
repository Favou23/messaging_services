
from django.db import models

class ChatRoom(models.Model):
    """Store user IDs as strings - users live in auth service"""
    participant_a = models.CharField(max_length=255, db_index=True)
    participant_b = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = (('participant_a', 'participant_b'),)
        indexes = [
            models.Index(fields=['participant_a', 'participant_b']),
        ]
    
    def __str__(self):
        return f"Room: {self.participant_a} <-> {self.participant_b}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name="messages", on_delete=models.CASCADE)
    sender_id = models.CharField(max_length=255)  # User ID from auth service
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('timestamp',)
        indexes = [
            models.Index(fields=['room', 'timestamp']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender_id} at {self.timestamp}"
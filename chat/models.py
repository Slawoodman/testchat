from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Thread(models.Model):
    participants = models.ManyToManyField(User, related_name="participants")
    created = models.DateTimeField(default=timezone.now())
    updated = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return str(f"Thread created - {self.id}")


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=500, blank=False, null=False)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now())
    is_read = models.BooleanField(default=False)

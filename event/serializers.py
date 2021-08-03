from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('penyelenggara', 'nama', 'deskripsi', 'dibuat')
        model = Event

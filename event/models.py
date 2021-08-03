from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    penyelenggara = models.CharField(max_length=100)
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField()
    dibuat = models.DateTimeField(auto_now_add=True)
    diupdate = models.DateTimeField(auto_now=True)
    panitia = models.ForeignKey(User, on_delete=models.CASCADE) #OneToMany?

    def __str__(self):
        return self.nama


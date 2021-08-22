from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    is_committee = models.BooleanField(
        'committee status',
        default=False,
        help_text='Committee can CRUD jury, RUD event, CRUD Score, and CRUD participants',
    )
    is_jury = models.BooleanField(
        'jury status',
        default=False,
        help_text='Jury can CRUD Score for every participants',
    )
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=1000, null=True, blank=True)
    city = models.CharField(max_length=512, null=True, blank=True)
    state = models.CharField(max_length=512, null=True, blank=True)
    photo_url = models.URLField(null=True, blank=True)

class Participants(models.Model):
    code = models.CharField(max_length=20, unique=True, null=False)
    full_name = models.CharField(max_length=512, null=False, blank=False)
    age = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    institute = models.CharField(max_length=512)
    total_score = models.FloatField(null=True)
    score_field = models.JSONField(null=True)
    photo_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

class Jury(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    participants = models.ManyToManyField(Participants, null=True, related_name='jury')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class Committee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=512)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)
    max_participants = models.IntegerField()
    num_jury = models.IntegerField()
    num_committee = models.IntegerField()
    event_level = models.CharField(max_length=512)
    panitia = models.ManyToManyField(Committee, null=True, related_name='event')
    juri = models.ManyToManyField(Jury, null=True, related_name='event')
    peserta = models.ManyToManyField(Participants, null=True, related_name='event')

    def __str__(self):
        return self.title



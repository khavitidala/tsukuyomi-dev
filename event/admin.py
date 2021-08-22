from django.contrib import admin
from .models import Event, Committee, Jury, Participants, User

admin.site.register(Event)
admin.site.register(Committee)
admin.site.register(Jury)
admin.site.register(Participants)
admin.site.register(User)


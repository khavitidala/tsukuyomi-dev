from django.urls import path
from .views import *

urlpatterns = [
    path('event/', EventList.as_view(), name='event-list'),
    path('event/committee/<int:pk>/', EventListFromCommittee.as_view(), name='event-list-from-committee'),
    path('event/jury/<int:pk>/', EventListFromJury.as_view(), name='event-list-from-jury'),
    path('event/<int:pk>/', EventDetail.as_view(), name='event-detail'),
    path('event/<int:eid>/committee/', CommitteeList.as_view(), name='committee-list'),
    path('event/<int:eid>/committee/<int:pk>/', CommitteeDetail().as_view(), name='committee-detail'),
    path('event/<int:eid>/jury/', JuryList.as_view(), name='jury-list'),
    path('event/<int:eid>/jury/<int:pk>/', JuryDetail.as_view(), name='jury-detail'),
    path('event/<int:eid>/participants/', ParticipantsList.as_view(), name='participants-list'),
    path('event/<int:eid>/jury/<int:jid>/participants/', ParticipantsJuryList.as_view(), name='participants-jury-list'),
    path('event/<int:eid>/jury/<int:jid>/participants/<int:pk>/', ParticipantsJuryDetail.as_view(), name='participants-jury-detail'),
]

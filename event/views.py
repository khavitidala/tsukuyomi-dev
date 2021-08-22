from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from .models import Committee, Jury, Event
from .exception_handler import get_response
from .serializers import *
from .permissions import *

class EventList(generics.ListCreateAPIView):
    """
    Menampilkan daftar dan membuat event, serta menampilkan statistik dari event.
    """
    permission_classes = (IsAdminUser,)
    queryset = Event.objects.all()
    serializer_class = EventBaseSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(get_response(message="Success", data={
            "statistic": {
                "total_event": Event.objects.all().count(),
                "total_participants": Participants.objects.all().count(),
                "total_jury": Jury.objects.all().count(),
                "total_committee": Committee.objects.all().count()
            },
            "list_event": serializer.data
        }, status=True))


class EventListFromCommittee(EventList):
    """
    Menampilkan daftar event pada Committee tertentu
    """
    permission_classes = (IsCommittee,)
    serializer_class = EventSerializer

    def get_queryset(self):
        pkcom = self.kwargs.get(self.lookup_field)
        return Event.objects.filter(panitia__pk=pkcom)

class EventListFromJury(EventList):
    """
    Menampilkan daftar event pada juri tertentu
    """
    permission_classes = (IsJury,)
    serializer_class = EventSerializer

    def get_queryset(self):
        pkjury = self.kwargs.get(self.lookup_field)
        return Event.objects.filter(juri__pk=pkjury)

class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Menampilkan detai event, update, dan delete event
    """
    permission_classes = (IsAdminOrCommitteeOrReadOnly,)
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class CommitteeList(generics.ListCreateAPIView):
    """
    Menampilkan daftar dan membuat akun committee
    catatan:
    jika respons API adalah pending, maka kemungkinan committee tsb.
    sudah terdaftar pada event lain. Maka, tambahkan jendela konfirmasi
    jika memang committee yg ada mau ditambahkan ke event tsb
    tambahkan query params ?confirm=1 dengan request POST dan body yang sama
    """
    permission_classes = (IsAdminUser,)
    serializer_class = CommitteeSerializer
    lookup_url_kwarg = 'eid'

    def get_queryset(self):
        eventId = self.kwargs['eid']
        return Committee.objects.filter(event__pk=eventId)
    
    def get_serializer_context(self):
        context = super(CommitteeList, self).get_serializer_context()
        context.update({
            'eid': self.kwargs.get(self.lookup_url_kwarg)
        })
        return context
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(get_response(message="Success", data=serializer.data, status=True))
    
    def post(self, request, *args, **kwargs):
        try:
            uname = User.objects.get(username=request.data["user"]["username"])
            try:
                confirm = request.query_params["confirm"]
                if confirm == "1":
                    lanjut = False
            except KeyError:
                return Response(get_response(message="Pending", data={
                    "yes": "event/"+str(self.kwargs['eid'])+"/committee/?confirm=1"
                }, status=False))
        except ObjectDoesNotExist:
            lanjut = True
        if lanjut:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        else:
            com = Committee.objects.get(user__username=request.data["user"]["username"])
            ev = Event.objects.get(pk=self.kwargs["eid"])
            ev.panitia.add(com)
            ev.save()
            
            return Response(get_response(message="Success", data={
                "id": com.id,
                "username": com.user.username,
                "first_name": com.user.first_name,
                "last_name": com.user.last_name
            }, status=True, status_code=200))

class CommitteeDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Menampilkan detail, update, dan delete committe tertentu
    """
    permission_classes = (IsAdminOrCommitteeOrReadOnly,)
    serializer_class = CommitteeDetailSerializer
    queryset = Committee.objects.all()

class JuryList(generics.ListCreateAPIView):
    """
    Menampilkan daftar dan membuat akun jury
    catatan:
    jika respons API adalah pending, maka kemungkinan jury tsb.
    sudah terdaftar pada event lain. Maka, tambahkan jendela konfirmasi
    jika memang jury yg ada mau ditambahkan ke event tsb
    tambahkan query params ?confirm=1 dengan request POST dan body yang sama
    """
    permission_classes = (IsAdminOrCommitteeOrReadOnly,)
    serializer_class = JurySerializer
    lookup_url_kwarg = 'eid'

    def get_queryset(self):
        eventId = self.kwargs['eid']
        return Jury.objects.filter(event__pk=eventId)
    
    def get_serializer_context(self):
        context = super(JuryList, self).get_serializer_context()
        context.update({
            'eid': self.kwargs.get(self.lookup_url_kwarg)
        })
        return context
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(get_response(message="Success", data=serializer.data, status=True))
    
    def post(self, request, *args, **kwargs):
        try:
            uname = User.objects.get(username=request.data["user"]["username"])
            try:
                confirm = request.query_params["confirm"]
                if confirm == "1":
                    lanjut = False
            except KeyError:
                return Response(get_response(message="Pending", data={
                    "yes": "event/"+str(self.kwargs['eid'])+"/committee/?confirm=1"
                }, status=False))
        except ObjectDoesNotExist:
            lanjut = True
        if lanjut:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        else:
            com = Jury.objects.get(user__username=request.data["user"]["username"])
            ev = Event.objects.get(pk=self.kwargs["eid"])
            ev.juri.add(com)
            ev.save()
            
            return Response(get_response(message="Success", data={
                "id": com.id,
                "username": com.user.username,
                "first_name": com.user.first_name,
                "last_name": com.user.last_name
            }, status=True, status_code=200))

class JuryDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Menampilkan detail, update, dan delete jury tertentu
    """
    permission_classes = (IsAdminOrCommitteeOrReadOnly,)
    serializer_class = JuryDetailSerializer
    queryset = Jury.objects.all()

class ParticipantsList(generics.ListAPIView):
    """
    Menampilkan daftar peserta yang diurutkan berdasarkan total_score. 
    Peserta yang ditampilkan berdasarkan id dari event yang diberikan
    """
    permission_classes = (IsAdminOrCommitteeOrReadOnly,)
    serializer_class = ParticipantsSerializer
    lookup_url_kwarg = 'eid'

    def get_queryset(self):
        eventId = self.kwargs['eid']
        return Participants.objects.filter(event__pk=eventId).order_by('-total_score')
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(get_response(message="Success", data=serializer.data, status=True))

class ParticipantsJuryList(generics.ListAPIView):
    """
    Menampilkan daftar participants berdasarkan jury tertentu
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ParticipantsSerializer
    lookup_url_kwarg = 'eid'

    def get_queryset(self):
        eventId = self.kwargs['eid']
        juryId = self.kwargs['jid']
        return Participants.objects.filter(event__pk=eventId ,jury__pk=juryId)

    def get_serializer_context(self):
        context = super(ParticipantsJuryList, self).get_serializer_context()
        context.update({
            'eid': self.kwargs.get(self.lookup_url_kwarg),
            'jid' : self.kwargs.get('jid')
        })
        return context
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(get_response(message="Success", data=serializer.data, status=True))

class ParticipantsJuryList(generics.CreateAPIView):
    """
    Membuat data participants sekaligus mengassign participants tsb ke jury tertentu. 
    Namun, untuk field score_field tidak bisa diisi saat pembuatan,
    field tsb. hanya bisa diupdate oleh jury yang bersangkutan
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ParticipantsCreateJurySerializer
    lookup_url_kwarg = 'eid'

    def get_queryset(self):
        eventId = self.kwargs['eid']
        juryId = self.kwargs['jid']
        return Participants.objects.filter(event__pk=eventId ,jury__pk=juryId)

    def get_serializer_context(self):
        context = super(ParticipantsJuryList, self).get_serializer_context()
        context.update({
            'eid': self.kwargs.get(self.lookup_url_kwarg),
            'jid' : self.kwargs.get('jid')
        })
        return context

class ParticipantsJuryDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Mengupdate, menampilkan detail, dan menghapus participants.
    Hal ini hanya bisa dilakukan oleh jury yang sudah diassgin sebelumnya
    """
    permission_classes = (IsSameJuryAndParticipantsOrReadOnly,)
    serializer_class = ParticipantsJurySerializer
    queryset = Participants.objects.all()

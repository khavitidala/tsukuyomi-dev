from rest_framework import serializers
from django.conf import settings
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist
from .models import Event, Committee, Jury, Participants, User
from .exception_handler import get_response
from .permissions import IsSameJuryAndParticipantsOrReadOnly

class CreateUser:
    def __init__(self, user_data):
        self.user_data = user_data

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(get_response(message="password tidak sesuai", status=False, status_code=400))

        return attrs
    
    def create_user(self):
        if self.user_data["username"] and self.user_data["password"] and self.user_data["password2"]:
            pw1 = self.user_data.pop('password')
            pw2 = self.user_data.pop('password2')
            
            user = User.objects.create(**self.user_data)
            passw = self.validate({'password':pw1, 'password2': pw2})
            user.set_password(passw['password'])
        else:
            raise serializers.ValidationError(get_response(message="username dan password harus diisi", status=False, status_code=400))
        return user

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    is_committee = serializers.BooleanField(read_only=True)
    is_jury = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id','first_name','last_name','phone_number','address','city','state','photo_url' ,'username', 'email', 'is_committee', 'is_jury', 'is_staff','password2', 'password',)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = CreateUser(**validated_data)

        return user.create_user()

class ParticipantsSerializer(serializers.ModelSerializer):
    score_field = serializers.JSONField(read_only=True)

    class Meta:
        fields = ('id', 'code', 'full_name','age','email','institute','total_score', 'score_field','photo_url', 'created_at', 'updated_at')
        model = Participants
    
    def create(self, validated_data):
        eid = self.context.get("eid", "")
        if eid:
            ev = Event.objects.get(pk=eid)
            p_count = Participants.objects.filter(event__pk=eid).count()
            if p_count < ev.max_participants:
                com = Participants.objects.create(**validated_data)
                com.save()
                jid = self.context.get("jid", "")
                ev.peserta.add(com)
                ev.save()
                if jid:
                    ju = Jury.objects.get(pk=jid)
                    ju.participants.add(com)
                    ju.save()
            else:
                raise serializers.ValidationError(get_response(message="Jumlah peserta sudah penuh", status=False, status_code=400))
        else:
            raise serializers.ValidationError(get_response(message="Event tidak ditemukan", status=False, status_code=400))
        return com
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)

        return repr

class ParticipantsJurySerializer(ParticipantsSerializer):
    score_field = serializers.JSONField(read_only=False)

    class Meta:
        fields = ('id', 'code', 'full_name','age','email','institute','total_score','score_field','photo_url', 'created_at', 'updated_at')
        model = Participants

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        out = get_response(message="Success", data=repr, status=True)

        return out


class ParticipantsCreateJurySerializer(ParticipantsSerializer):

    class Meta:
        fields = ('id', 'code', 'full_name','age','email','institute','total_score','score_field','photo_url', 'created_at', 'updated_at')
        model = Participants

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        out = get_response(message="Success", data=repr, status=True)

        return out

class JurySerializer(serializers.ModelSerializer):
    participants = ParticipantsSerializer(read_only=True, many=True, required=False)
    user = UserSerializer(write_only=True)

    class Meta:
        fields = ('id', 'participants', 'created_at', 'updated_at', 'user')
        model = Jury

    def create(self, validated_data):
        eid = self.context.get("eid", "")
        if eid:
            ev = Event.objects.get(pk=eid)
            ju_count = Jury.objects.filter(event__pk=eid).count()
            if ju_count < ev.num_jury:
                user_data = validated_data.pop('user')
                user = CreateUser(user_data)
                u = user.create_user()
                u.is_jury = True
                u.save()
                com = Jury.objects.create(user=u, **validated_data)
                com.save()
                ev.juri.add(com)
                ev.save()
            else:
                raise serializers.ValidationError(get_response(message="Jumlah juri sudah penuh", status=False, status_code=400))
        else:
            raise serializers.ValidationError(get_response(message="Event tidak ditemukan", status=False, status_code=400))
        return com
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)

        return repr

class JuryDetailSerializer(serializers.ModelSerializer):
    participants = ParticipantsSerializer(read_only=True, many=True)
    user = UserSerializer(read_only=True)

    class Meta:
        fields = ('id', 'participants', 'created_at', 'updated_at', 'user')
        model = Jury
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        out = get_response(message="Success", data=repr, status=True)

        return out

class CommitteeSerializer(serializers.ModelSerializer):
    user = UserSerializer(write_only=True)

    class Meta:
        fields = ('id', 'created_at', 'updated_at', 'user')
        model = Committee

    def create(self, validated_data):
        eid = self.context.get("eid", "")
        if eid:
            ev = Event.objects.get(pk=eid)
            com_count = Committee.objects.filter(event__pk=eid).count()
            if com_count < ev.num_committee:
                user_data = validated_data.pop('user')
                user = CreateUser(user_data)
                u = user.create_user()
                status = self.context["request"].user
                if status.is_staff:
                    u.is_committee = True
                    u.save()
                com = Committee.objects.create(user=u, **validated_data)
                com.save()
                ev.panitia.add(com)
                ev.save()
            else:
                raise serializers.ValidationError(get_response(message="Jumlah juri sudah penuh", status=False, status_code=400))
        else:
            raise serializers.ValidationError(get_response(message="Event tidak ditemukan", status=False, status_code=400))
        return com
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["first_name"] = instance.user.first_name
        repr["last_name"] = instance.user.last_name

        return repr

class CommitteeDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        fields = ('id', 'user' ,'created_at', 'updated_at')
        model = Committee
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        out = get_response(message="Success", data=repr, status=True)

        return out
    

class EventBaseSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    panitia = CommitteeSerializer(many=True, required=False, read_only=True)
    juri = JurySerializer(many=True, required=False, read_only=True)
    peserta = ParticipantsSerializer(many=True, required=False, read_only=True)

    class Meta:
        fields = ('id','user', 'title', 'start_date', 'end_date','start_time', 'end_time',
                  'max_participants','num_jury','num_committee','event_level', 'panitia', 'juri', 'peserta')
        model = Event

class EventSerializer(EventBaseSerializer):

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if self.context.get("eid", ""):
            prk = self.context.get("eid", "")
            repr['current_total_participants'] = Participants.objects.filter(event__pk=prk).count()
            repr['current_total_jury'] = Jury.objects.filter(event__pk=prk).count()
        return repr

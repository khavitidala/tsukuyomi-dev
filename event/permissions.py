from rest_framework import permissions
from .models import Jury
from django.core.exceptions import ObjectDoesNotExist

class IsSameJuryAndParticipantsOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            juri = Jury.objects.get(participants=obj)
            return True
        except ObjectDoesNotExist:
            return False

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class IsCommittee(permissions.BasePermission):
    """
    Allows access only to committee.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_committee)

class IsAdminOrCommitteeOrReadOnly(permissions.BasePermission):
    """
    Allows access only to admin or Committee users.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return bool(request.user and request.user.is_staff) or bool(request.user and request.user.is_committee)

class IsJury(permissions.BasePermission):
    """
    Allows access only to jury.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_jury)

class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.user == request.user
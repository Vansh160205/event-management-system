from rest_framework.permissions import BasePermission, SAFE_METHODS

# Restricts update/delete actions to event organizer only
class IsOrganizerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.organizer == request.user


# Allows viewing if event is public, user is invited, or organizer
class IsInvitedOrPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.organizer == request.user:
            return True

        if obj.is_public and request.method in SAFE_METHODS:
            return True

        if request.method in SAFE_METHODS and request.user.is_authenticated:
            return request.user in obj.invited.all()

        return False

# events/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOrganizerOrReadOnly(BasePermission):
    """
    Allow read-only for everyone (handled in viewset list),
    but only organizer can update/delete.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.organizer == request.user


class IsInvitedOrPublic(BasePermission):
    """
    Allow access if:
    - event is public
    - OR user is the organizer
    - OR user is in event.invited
    For unsafe methods, organizer permission still required (combine with IsOrganizerOrReadOnly).
    """
    def has_object_permission(self, request, view, obj):
        # organizers always allowed
        if obj.organizer == request.user:
            return True

        # public events allowed for safe methods
        if obj.is_public and request.method in SAFE_METHODS:
            return True

        # invited users may view (safe methods)
        if request.method in SAFE_METHODS and request.user.is_authenticated:
            try:
                return request.user in obj.invited.all()
            except Exception:
                # defensive: if anything goes wrong, deny
                return False

        # default deny
        return False

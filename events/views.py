from rest_framework import viewsets, generics, permissions, status
from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsInvitedOrPublic
from rest_framework.decorators import action
from rest_framework.response import Response

# in events/views.py

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly, IsInvitedOrPublic]

    def get_queryset(self):
        """
        - list: return public events only
        - otherwise: allow all (object permissions will filter access)
        """
        if self.action == 'list':
            return Event.objects.filter(is_public=True).order_by('id')
        return Event.objects.all().order_by('id')

    def get_object(self):
        obj = super().get_object()
        # run object-level permission checks (this throws PermissionDenied if not allowed)
        for permission in self.get_permissions():
            if not permission.has_object_permission(self.request, self, obj):
                self.permission_denied(self.request, message="You do not have access to this event.")
        return obj

    def perform_create(self, serializer):
        # organizer is always the request.user
        serializer.save(organizer=self.request.user)

# in events/views.py

# Rename this to be more accurate
class RSVPViewSet(generics.GenericAPIView): # Change from CreateAPIView
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        event = generics.get_object_or_404(Event, id=self.kwargs['event_id'])
        rsvp_status = request.data.get('status') # <-- Renamed to avoid conflict

        if rsvp_status not in ['Going', 'Maybe', 'Not Going']:
            return Response(
                {"error": "Status must be 'Going', 'Maybe', or 'Not Going'."}, 
                status=status.HTTP_400_BAD_REQUEST # <-- Use the status module
            )

        rsvp, created = RSVP.objects.update_or_create(
            user=self.request.user,
            event=event,
            defaults={'status': rsvp_status} # <-- Use the renamed variable
        )

        serializer = self.get_serializer(rsvp)
        http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK # <-- Use status module
        return Response(serializer.data, status=http_status)
    

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(event_id=self.kwargs['event_id']).order_by('id')

    def perform_create(self, serializer):
        event_id = self.kwargs['event_id']
        serializer.save(event_id=event_id, user=self.request.user)

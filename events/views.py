from rest_framework import viewsets, generics, permissions, status
from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsInvitedOrPublic
from rest_framework.response import Response


# Handles all CRUD operations for Events
class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly, IsInvitedOrPublic]

    def get_queryset(self):
        # Public events for listing, full access for object-level
        if self.action == 'list':
            return Event.objects.filter(is_public=True).order_by('id')
        return Event.objects.all().order_by('id')

    def get_object(self):
        obj = super().get_object()
        # Enforce object-level permission check
        for permission in self.get_permissions():
            if not permission.has_object_permission(self.request, self, obj):
                self.permission_denied(self.request, message="You do not have access to this event.")
        return obj

    def perform_create(self, serializer):
        # Automatically set event organizer as the current user
        serializer.save(organizer=self.request.user)


# Creates or updates RSVP for authenticated user
class RSVPViewSet(generics.GenericAPIView):
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        event = generics.get_object_or_404(Event, id=self.kwargs['event_id'])
        rsvp_status = request.data.get('status')

        if rsvp_status not in ['Going', 'Maybe', 'Not Going']:
            return Response({"error": "Status must be 'Going', 'Maybe', or 'Not Going'."},
                            status=status.HTTP_400_BAD_REQUEST)

        rsvp, created = RSVP.objects.update_or_create(
            user=self.request.user,
            event=event,
            defaults={'status': rsvp_status}
        )

        serializer = self.get_serializer(rsvp)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# Lists all reviews for an event or allows adding one
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(event_id=self.kwargs['event_id']).order_by('id')

    def perform_create(self, serializer):
        serializer.save(event_id=self.kwargs['event_id'], user=self.request.user)

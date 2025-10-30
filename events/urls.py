from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPViewSet, ReviewListCreateView

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('events/<int:event_id>/rsvp/', RSVPViewSet.as_view(), name='event-rsvp'),
    path('events/<int:event_id>/reviews/', ReviewListCreateView.as_view(), name='event-reviews'),
]

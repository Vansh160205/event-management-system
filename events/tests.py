from django.contrib.auth import get_user_model # <-- CHANGED THIS LINE
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Event, RSVP, Review

User = get_user_model() # <-- ADDED THIS LINE


class EventManagementTests(APITestCase):
    def setUp(self):
        # Create users (This will now use your UserProfile model)
        self.user = User.objects.create_user(username="user1", password="pass1234")
        self.user2 = User.objects.create_user(username="user2", password="pass1234")

        # Authenticate user1
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'user1',
            'password': 'pass1234'
        })
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create an event by user1
        self.event_data = {
            "title": "Tech Conference",
            "description": "A great event for tech enthusiasts",
            "location": "Mumbai",
            "start_time": "2025-11-10T09:00:00Z",
            "end_time": "2025-11-10T17:00:00Z",
            "is_public": True
        }
        self.event = Event.objects.create(organizer=self.user, **self.event_data)

    # ------------------- Event Tests -------------------

    def test_create_event(self):
        """Test event creation by an authenticated user"""
        data = {
            "title": "Hackathon 2025",
            "description": "Coding challenge",
            "location": "Pune",
            "start_time": "2025-12-01T09:00:00Z",
            "end_time": "2025-12-01T17:00:00Z",
            "is_public": True
        }
        response = self.client.post(reverse('event-list'), data, format='json') # Using reverse()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(response.data['title'], "Hackathon 2025")

    def test_list_events(self):
        """Test retrieving list of public events"""
        response = self.client.get(reverse('event-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Note: If you add pagination, this check will change
        self.assertGreaterEqual(len(response.data), 1)

    def test_event_detail(self):
        """Test retrieving single event details"""
        response = self.client.get(reverse('event-detail', kwargs={'pk': self.event.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Tech Conference")

    def test_update_event_by_organizer(self):
        """Organizer should be able to update their event"""
        updated = {**self.event_data, "title": "Updated Tech Conference"}
        response = self.client.put(
            reverse('event-detail', kwargs={'pk': self.event.id}), 
            updated, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Updated Tech Conference")

    def test_update_event_by_non_organizer_forbidden(self):
        """Another user should not be allowed to edit"""
        # Authenticate as user2
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'user2',
            'password': 'pass1234'
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        updated = {"title": "Hacked Event", **self.event_data}
        response = self.client.put(
            reverse('event-detail', kwargs={'pk': self.event.id}), 
            updated, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------- RSVP Tests -------------------

    def test_rsvp_event(self):
        """Test RSVP to an event"""
        data = {"status": "Going"}
        response = self.client.post(
            reverse('event-rsvp', kwargs={'event_id': self.event.id}), 
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RSVP.objects.count(), 1)
        self.assertEqual(RSVP.objects.first().status, "Going")

    # ------------------- Review Tests -------------------

    def test_add_review(self):
        """Test adding a review to an event"""
        data = {"rating": 5, "comment": "Fantastic event!"}
        response = self.client.post(
            reverse('event-reviews', kwargs={'event_id': self.event.id}), 
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().rating, 5)

    def test_list_reviews(self):
        """Test listing all reviews for an event"""
        Review.objects.create(event=self.event, user=self.user, rating=4, comment="Nice!")
        response = self.client.get(reverse('event-reviews', kwargs={'event_id': self.event.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_private_event_invite_access(self):
        """Private event should only be viewable by invited users and organizer"""
        # Make event private
        self.event.is_public = False
        self.event.save()

        # user2 should NOT be able to view initially
        # authenticate as user2
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'user2',
            'password': 'pass1234'
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        resp = self.client.get(reverse('event-detail', kwargs={'pk': self.event.id}))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # Invite user2
        self.event.invited.add(self.user2)

        resp = self.client.get(reverse('event-detail', kwargs={'pk': self.event.id}))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Cleanup: authenticate back as user1 for following tests
        resp = self.client.post(reverse('token_obtain_pair'), {
            'username': 'user1',
            'password': 'pass1234'
        })
        token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_unauthenticated_cannot_create_event(self):
        """Ensure unauthenticated users cannot create events"""
        # clear auth
        self.client.credentials()  # removes Authorization header
        data = {
            "title": "Public Hack",
            "description": "test",
            "location": "Nowhere",
            "start_time": "2025-12-01T09:00:00Z",
            "end_time": "2025-12-01T17:00:00Z",
            "is_public": True
        }
        resp = self.client.post(reverse('event-list'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
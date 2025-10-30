from rest_framework import serializers
from .models import Event, RSVP, Review, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()


# Serializes user info for responses
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'full_name', 'bio', 'location')


# Main serializer for Event CRUD operations
class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.ReadOnlyField(source='organizer.username')
    invited = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)

    class Meta:
        model = Event
        fields = '__all__'


# Handles RSVP creation and retrieval
class RSVPSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    event = serializers.ReadOnlyField(source='event.id')

    class Meta:
        model = RSVP
        fields = '__all__'


# Handles event reviews and ratings
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    event = serializers.ReadOnlyField(source='event.id')

    class Meta:
        model = Review
        fields = '__all__'

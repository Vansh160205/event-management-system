from rest_framework import serializers
from .models import Event, RSVP, Review, UserProfile
from django.contrib.auth import get_user_model

# Get the active user model (which is your events.UserProfile)
User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile # This now correctly refers to your custom user model
        # Avoid '__all__' as it can expose sensitive data like password hashes
        fields = ('id', 'username', 'email', 'full_name', 'bio', 'location')


class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.ReadOnlyField(source='organizer.username')
    
    # --- THE FIX ---
    # The queryset must use the *active* user model (from get_user_model()),
    # not the old 'auth.User'.
    invited = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(), 
        required=False
    )
    # --- END FIX ---

    class Meta:
        model = Event
        fields = '__all__'


class RSVPSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    event = serializers.ReadOnlyField(source='event.id')  
    class Meta:
        model = RSVP
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    event = serializers.ReadOnlyField(source='event.id') 
    class Meta:
        model = Review
        fields = '__all__'
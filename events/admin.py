from django.contrib import admin
from .models import UserProfile, Event, RSVP, Review

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'location')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'is_public', 'start_time', 'end_time')
    search_fields = ('title', 'location', 'organizer__username')
    list_filter = ('is_public', 'location')

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status')
    list_filter = ('status',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'rating', 'created_at')
    list_filter = ('rating',)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# 1. UserProfile is now the main user model, inheriting from AbstractUser.
#    It includes all built-in Django user fields (username, email, etc.)
#    plus your custom fields.
class UserProfile(AbstractUser):
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.username


class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    
    # 2. Changed 'User' to 'settings.AUTH_USER_MODEL'
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events')
    
    location = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_public = models.BooleanField(default=True)
    
    # 3. Changed 'User' to 'settings.AUTH_USER_MODEL'
    invited = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='invited_events', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class RSVP(models.Model):
    STATUS_CHOICES = [
        ('Going', 'Going'),
        ('Maybe', 'Maybe'),
        ('Not Going', 'Not Going'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    
    # 4. Changed 'User' to 'settings.AUTH_USER_MODEL'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rsvps')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"
    
    # 5. Kept the unique_together constraint
    class Meta:
        unique_together = ('event', 'user')


class Review(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    
    # 6. Changed 'User' to 'settings.AUTH_USER_MODEL'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    
    rating =models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True) # Good for ordering

    def __str__(self):
        return f"Review by {self.user.username} for {self.event.title}"
    
    # 7. Kept the unique_together constraint
    class Meta:
        unique_together = ('event', 'user')
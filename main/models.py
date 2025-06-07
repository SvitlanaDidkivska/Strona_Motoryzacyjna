from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Car(models.Model):
    name = models.CharField(max_length=200)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50)
    drive_wheel = models.CharField(max_length=20, choices=[
        ('fwd', 'Front Wheel Drive'),
        ('rwd', 'Rear Wheel Drive'),
        ('4wd', '4 Wheel Drive'),
        ('awd', 'All Wheel Drive'),
    ])
    description = models.TextField()
    image = models.ImageField(upload_to='cars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New fields for NHTSA data
    vehicle_type = models.CharField(max_length=100, blank=True)
    fuel_type = models.CharField(max_length=50, blank=True)
    engine = models.CharField(max_length=100, blank=True)
    transmission = models.CharField(max_length=100, blank=True)
    doors = models.IntegerField(null=True, blank=True)
    seats = models.IntegerField(null=True, blank=True)
    manufacturer_code = models.CharField(max_length=50, blank=True)
    plant_country = models.CharField(max_length=100, blank=True)
    safety_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"

    class Meta:
        ordering = ['-created_at']

class Review(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'car')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    dark_mode = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    joined_date = models.DateTimeField(default=timezone.now)
    interests = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('post_created', 'Created a post'),
        ('comment_added', 'Added a comment'),
        ('badge_earned', 'Earned a badge'),
        ('car_reviewed', 'Reviewed a car'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User activities'

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

class Watch(models.Model):
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watching')
    watched = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watched_by')
    created_at = models.DateTimeField(auto_now_add=True)
    notify_on_post = models.BooleanField(default=True)
    notify_on_comment = models.BooleanField(default=True)
    notify_on_badge = models.BooleanField(default=True)

    class Meta:
        unique_together = ('watcher', 'watched')

    def __str__(self):
        return f"{self.watcher.username} watches {self.watched.username}"

    def create_notification(self, activity):
        """Create a notification for the watcher based on the watched user's activity."""
        if (activity.activity_type == 'post_created' and self.notify_on_post) or \
           (activity.activity_type == 'comment_added' and self.notify_on_comment) or \
           (activity.activity_type == 'badge_earned' and self.notify_on_badge):
            from forum.models import Notification
            Notification.objects.create(
                recipient=self.watcher,
                sender=self.watched,
                notification_type='activity',
                message=f"{self.watched.username} {activity.get_activity_type_display().lower()}",
                url=activity.url
            )

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile instance when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile instance when the User is saved."""
    instance.userprofile.save()

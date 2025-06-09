from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from forum.models import ForumPost, Comment, UserBadge
from .models import UserActivity, Watch, UserProfile

@receiver(post_save, sender=ForumPost)
def create_post_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance.author,
            activity_type='post_created',
            content=f'created a new post: {instance.title}',
            url=f'/forum/post/{instance.id}/'
        )
        # Create notifications for watchers
        for watch in Watch.objects.filter(watched=instance.author, notify_on_post=True):
            watch.create_notification(UserActivity.objects.get(
                user=instance.author,
                activity_type='post_created',
                content=f'created a new post: {instance.title}'
            ))

@receiver(post_save, sender=Comment)
def create_comment_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance.author,
            activity_type='comment_added',
            content=f'commented on {instance.post.title}',
            url=f'/forum/post/{instance.post.id}/'
        )
        # Create notifications for watchers
        for watch in Watch.objects.filter(watched=instance.author, notify_on_comment=True):
            watch.create_notification(UserActivity.objects.get(
                user=instance.author,
                activity_type='comment_added',
                content=f'commented on {instance.post.title}'
            ))

@receiver(post_save, sender=UserBadge)
def create_badge_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='badge_earned',
            content=f'earned the {instance.get_badge_type_display()} badge',
            url='/forum/badges/'
        )
        # Create notifications for watchers
        for watch in Watch.objects.filter(watched=instance.user, notify_on_badge=True):
            watch.create_notification(UserActivity.objects.get(
                user=instance.user,
                activity_type='badge_earned',
                content=f'earned the {instance.get_badge_type_display()} badge'
            ))

@receiver(post_save, sender=Watch)
def create_watch_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance.watcher,
            activity_type='started_watching',
            content=f'started watching {instance.watched.username}',
            url=f'/user/{instance.watched.username}/'
        )

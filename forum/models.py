from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ForumCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Forum Categories"

class ForumPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mentioned_users = models.ManyToManyField(User, related_name='mentioned_in_posts', blank=True)
    reactions = models.ManyToManyField(User, through='PostReaction', related_name='post_reactions')

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='comment_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mentioned_users = models.ManyToManyField(User, related_name='mentioned_in_comments', blank=True)
    reactions = models.ManyToManyField(User, through='CommentReaction', related_name='comment_reactions')

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

class Notification(models.Model):
    MENTION = 'mention'
    REACTION = 'reaction'
    COMMENT = 'comment'
    
    NOTIFICATION_TYPES = [
        (MENTION, 'Mention'),
        (REACTION, 'Reaction'),
        (COMMENT, 'Comment'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notification to {self.recipient.username} from {self.sender.username}: {self.message}"

class Reaction(models.Model):
    LIKE = 'like'
    LOVE = 'love'
    HAHA = 'haha'
    WOW = 'wow'
    SAD = 'sad'
    ANGRY = 'angry'
    
    REACTION_TYPES = [
        (LIKE, '👍'),
        (LOVE, '❤️'),
        (HAHA, '😄'),
        (WOW, '😮'),
        (SAD, '😢'),
        (ANGRY, '😠'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class PostReaction(Reaction):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post')

class CommentReaction(Reaction):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'comment')

class UserBadge(models.Model):
    NEWCOMER = 'newcomer'
    REGULAR = 'regular'
    CONTRIBUTOR = 'contributor'
    EXPERT = 'expert'
    MODERATOR = 'moderator'
    
    BADGE_TYPES = [
        (NEWCOMER, 'Newcomer'),
        (REGULAR, 'Regular'),
        (CONTRIBUTOR, 'Contributor'),
        (EXPERT, 'Expert'),
        (MODERATOR, 'Moderator'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge_type')

    def __str__(self):
        return f"{self.user.username}'s {self.get_badge_type_display()} badge"

class UserReputation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reputation')
    points = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s reputation: {self.points} points"

import re
from django.contrib.auth.models import User
from .models import Notification

def extract_mentions(content):
    """Extract mentioned usernames from content"""
    # Match @username pattern
    mentions = re.findall(r'@(\w+)', content)
    return list(set(mentions))  # Remove duplicates

def process_mentions(content, sender, post=None, comment=None):
    """Process mentions in content and create notifications"""
    mentioned_users = []
    usernames = extract_mentions(content)
    
    if not usernames:
        return mentioned_users

    # Find existing users from mentioned usernames
    users = User.objects.filter(username__in=usernames)
    
    for user in users:
        if user != sender:  # Don't notify the sender
            # Create notification
            if post:
                message = f"{sender.username} mentioned you in a post"
                url = f"/forum/post/{post.id}/"
            elif comment:
                message = f"{sender.username} mentioned you in a comment"
                url = f"/forum/post/{comment.post.id}/"
            
            Notification.objects.create(
                recipient=user,
                sender=sender,
                notification_type='mention',
                message=message,
                url=url
            )
            mentioned_users.append(user)
    
    return mentioned_users

def create_reaction_notification(user, target_user, reaction_type, post=None, comment=None):
    """Create notification for reactions"""
    if user == target_user:  # Don't notify the user about their own reactions
        return

    if post:
        message = f"{user.username} reacted with {reaction_type} to your post"
        url = f"/forum/post/{post.id}/"
    elif comment:
        message = f"{user.username} reacted with {reaction_type} to your comment"
        url = f"/forum/post/{comment.post.id}/"

    Notification.objects.create(
        recipient=target_user,
        sender=user,
        notification_type='reaction',
        message=message,
        url=url
    )

def update_user_reputation(user, action_type):
    """Update user reputation based on actions"""
    points = {
        'post_created': 5,
        'post_liked': 2,
        'comment_created': 3,
        'comment_liked': 1,
        'post_deleted': -2,
        'comment_deleted': -1
    }

    if action_type in points:
        reputation, created = None, False
        try:
            reputation = user.reputation
        except Exception:
            from .models import UserReputation
            reputation = UserReputation.objects.create(user=user, points=0)
            created = True

        if reputation:
            reputation.points += points[action_type]
            reputation.save()

def check_and_award_badges(user):
    """Check and award badges based on user's activity and reputation"""
    reputation = user.reputation.points if hasattr(user, 'reputation') else 0
    posts_count = user.forumpost_set.count()
    comments_count = user.comment_set.count()

    # Define badge criteria
    badge_criteria = {
        'newcomer': {'reputation': 0, 'posts': 1},
        'regular': {'reputation': 50, 'posts': 5},
        'contributor': {'reputation': 100, 'posts': 10},
        'expert': {'reputation': 200, 'posts': 20},
    }

    from .models import UserBadge
    
    for badge_type, criteria in badge_criteria.items():
        if (reputation >= criteria['reputation'] and 
            posts_count >= criteria['posts'] and 
            not user.badges.filter(badge_type=badge_type).exists()):
            
            UserBadge.objects.create(user=user, badge_type=badge_type)

from django.shortcuts import render
from .models import ForumCategory, ForumPost

def index(request):
    categories = ForumCategory.objects.all()
    recent_posts = ForumPost.objects.all().order_by('-created_at')[:5]  # Get the 5 most recent posts
    context = {
        'categories': categories,
        'recent_posts': recent_posts
    }
    return render(request, 'forum/index.html', context)

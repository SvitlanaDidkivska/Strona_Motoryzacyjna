from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid
from django.db.models import Q
from .models import ForumCategory, ForumPost, Comment, CommentReaction, UserBadge
from .forms import ForumPostForm, CommentForm, ForumCategoryForm
from .utils import process_mentions, update_user_reputation, check_and_award_badges

def index(request):
    categories = ForumCategory.objects.all()
    recent_posts = ForumPost.objects.select_related('author', 'category').order_by('-created_at')[:5]

    query = request.GET.get('q')
    if query:
        all_posts = ForumPost.objects.select_related('author', 'category').filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-created_at')
    else:
        all_posts = ForumPost.objects.select_related('author', 'category').order_by('-created_at')

    paginator = Paginator(all_posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'recent_posts': recent_posts,
        'posts': posts,
        'query': query,
    }
    return render(request, 'forum/index.html', context)

def category_detail(request, category_id):
    category = get_object_or_404(ForumCategory, id=category_id)
    posts = category.posts.select_related('author').order_by('-created_at')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'forum/category_detail.html', context)

def post_detail(request, post_id):
    post = get_object_or_404(ForumPost.objects.select_related('author', 'category'), id=post_id)
    comments = post.comments.select_related('author').order_by('created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

            # Process mentions
            mentioned_users = process_mentions(comment.content, request.user, comment=comment)
            if mentioned_users:
                comment.mentioned_users.add(*mentioned_users)

            # Update reputation and check badges
            update_user_reputation(request.user, 'comment_created')
            check_and_award_badges(request.user)

            messages.success(request, 'Comment added successfully!')
            return redirect('forum:post_detail', post_id=post.id)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'forum/post_detail.html', context)

@login_required
@require_POST
def add_comment_reaction(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    reaction_type = request.POST.get('reaction_type')
    
    if reaction_type not in dict(CommentReaction.REACTION_TYPES):
        return JsonResponse({'error': 'Invalid reaction type'}, status=400)

    reaction, created = CommentReaction.objects.get_or_create(
        user=request.user,
        comment=comment,
        defaults={'reaction_type': reaction_type}
    )

    if not created:
        if reaction.reaction_type == reaction_type:
            reaction.delete()
            update_user_reputation(comment.author, 'comment_liked')
            return JsonResponse({'status': 'removed'})
        else:
            reaction.reaction_type = reaction_type
            reaction.save()

    # Update reputation for comment author
    update_user_reputation(comment.author, 'comment_liked')
    check_and_award_badges(comment.author)

    return JsonResponse({
        'status': 'added' if created else 'updated',
        'reaction_type': reaction_type
    })

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.user != post.author:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        form = ForumPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = ForumPostForm(instance=post)
    
    return render(request, 'forum/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.user != post.author:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('index')
    
    return render(request, 'forum/delete_post.html', {'post': post})

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        messages.error(request, 'You can only edit your own comments.')
        return redirect('post_detail', post_id=comment.post.id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully!')
            return redirect('post_detail', post_id=comment.post.id)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'forum/edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        messages.error(request, 'You can only delete your own comments.')
        return redirect('post_detail', post_id=comment.post.id)
    
    if request.method == 'POST':
        post_id = comment.post.id
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('post_detail', post_id=post_id)
    
    return render(request, 'forum/delete_comment.html', {'comment': comment})

@login_required
def add_category(request):
    if not request.user.is_staff:
        messages.error(request, 'Only staff members can add categories.')
        return redirect('index')
    
    if request.method == 'POST':
        form = ForumCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('index')
    else:
        form = ForumCategoryForm()
    
    return render(request, 'forum/add_category.html', {'form': form})

@csrf_exempt
def comment_image_upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        image_file = request.FILES['file']
        # Generate a unique filename
        ext = os.path.splitext(image_file.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join('comment_images', filename)

        # Save the file
        saved_path = default_storage.save(file_path, ContentFile(image_file.read()))
        image_url = default_storage.url(saved_path)

        return JsonResponse({'location': image_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def badge_list(request):
    badges = UserBadge.BADGE_TYPES
    badge_descriptions = {
        'newcomer': {
            'description': 'Awarded when you join the community.',
            'requirements': 'Create an account on CarHub.',
            'color': 'bg-gray-600'
        },
        'regular': {
            'description': 'Awarded for consistent participation.',
            'requirements': 'Make at least 10 posts or comments.',
            'color': 'bg-blue-600'
        },
        'contributor': {
            'description': 'Awarded for contributing valuable content.',
            'requirements': 'Receive 50+ reputation points from your contributions.',
            'color': 'bg-green-600'
        },
        'expert': {
            'description': 'Awarded for expert knowledge and helpfulness.',
            'requirements': 'Receive 200+ reputation points and have at least one highly-rated answer.',
            'color': 'bg-purple-600'
        },
        'moderator': {
            'description': 'Awarded to site moderators and admins.',
            'requirements': 'Be appointed as a site moderator or administrator.',
            'color': 'bg-yellow-600'
        },
    }
    context = {
        'badges': badges,
        'badge_descriptions': badge_descriptions,
    }
    return render(request, 'forum/badge_list.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ForumPost, PostReaction, Comment
from .forms import ForumPostForm, CommentForm
from .utils import process_mentions, update_user_reputation, check_and_award_badges

@login_required
def add_post(request):
    if request.method == 'POST':
        form = ForumPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if not post.category:
                post.category = None
            post.save()

            # Process mentions
            mentioned_users = process_mentions(post.content, request.user, post=post)
            if mentioned_users:
                post.mentioned_users.add(*mentioned_users)

            # Update reputation and check badges
            update_user_reputation(request.user, 'post_created')
            check_and_award_badges(request.user)

            return redirect('forum:index')
    else:
        form = ForumPostForm()
    return render(request, 'forum/add_post.html', {'form': form})

@login_required
@require_POST
def add_post_reaction(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    reaction_type = request.POST.get('reaction_type')
    
    if reaction_type not in dict(PostReaction.REACTION_TYPES):
        return JsonResponse({'error': 'Invalid reaction type'}, status=400)

    reaction, created = PostReaction.objects.get_or_create(
        user=request.user,
        post=post,
        defaults={'reaction_type': reaction_type}
    )

    if not created:
        if reaction.reaction_type == reaction_type:
            reaction.delete()
            update_user_reputation(post.author, 'post_liked')
            return JsonResponse({'status': 'removed'})
        else:
            reaction.reaction_type = reaction_type
            reaction.save()

    # Update reputation for post author
    update_user_reputation(post.author, 'post_liked')
    check_and_award_badges(post.author)

    return JsonResponse({
        'status': 'added' if created else 'updated',
        'reaction_type': reaction_type
    })

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    comments = post.comments.all().order_by('created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
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

            # After saving comment, re-fetch comments and reset form
            comments = post.comments.all().order_by('created_at')
            form = CommentForm()
        else:
            # If form invalid, keep existing comments and form with errors
            comments = post.comments.all().order_by('created_at')
    else:
        form = CommentForm()
        comments = post.comments.all().order_by('created_at')

    return render(request, 'forum/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })

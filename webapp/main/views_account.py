from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .forms import UserProfileForm
from .models import Watch, UserActivity

@login_required
def account(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('main:account')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'main/account.html', {'form': form})

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_watching = False
    if request.user.is_authenticated:
        is_watching = Watch.objects.filter(watcher=request.user, watched=profile_user).exists()
    
    # Get user's own activities
    activities = UserActivity.objects.filter(user=profile_user).order_by('-created_at')[:5]
    
    # Get activities from watched users (only shown on user's own profile)
    watched_activities = []
    if request.user.is_authenticated and request.user == profile_user:
        watched_users = User.objects.filter(watched_by__watcher=profile_user)
        watched_activities = UserActivity.objects.filter(
            user__in=watched_users
        ).select_related('user').order_by('-created_at')[:10]
    
    context = {
        'profile_user': profile_user,
        'is_watching': is_watching,
        'activities': activities,
        'watched_activities': watched_activities,
    }
    return render(request, 'main/user_profile.html', context)

@login_required
@require_POST
def toggle_watch(request, username):
    user_to_watch = get_object_or_404(User, username=username)
    if user_to_watch == request.user:
        return JsonResponse({'error': "You cannot watch yourself."}, status=400)
    
    watch, created = Watch.objects.get_or_create(watcher=request.user, watched=user_to_watch)
    if not created:
        watch.delete()
        return JsonResponse({'status': 'unwatched'})
    
    # Create an activity for the new watch
    UserActivity.objects.create(
        user=request.user,
        activity_type='started_watching',
        content=f"started watching {user_to_watch.username}",
        url=f"/user/{user_to_watch.username}/"
    )
    
    return JsonResponse({'status': 'watched'})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ForumPostForm

@login_required
def add_post(request):
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if not post.category:
                post.category = None
            post.save()
            return redirect('forum:index')
    else:
        form = ForumPostForm()
    return render(request, 'forum/add_post.html', {'form': form})

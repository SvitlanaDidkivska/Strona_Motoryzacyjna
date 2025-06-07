from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q

def user_mentions(request):
    """API endpoint for user mentions autocomplete"""
    query = request.GET.get('q', '')
    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query)
    ).values('username', 'first_name', 'last_name')[:10]

    results = []
    for user in users:
        display_name = user['username']
        if user['first_name'] and user['last_name']:
            display_name = f"{user['first_name']} {user['last_name']} (@{user['username']})"
        results.append({
            'id': user['username'],
            'name': display_name
        })

    return JsonResponse({'results': results})

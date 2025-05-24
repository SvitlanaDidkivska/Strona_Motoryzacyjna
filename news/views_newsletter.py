from django.shortcuts import redirect
from django.contrib import messages
from .forms_newsletter import NewsletterForm

def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for subscribing to our newsletter!')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, 'Please enter a valid email address.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return redirect('/')

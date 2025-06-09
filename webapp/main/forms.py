from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Review, UserProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password help texts
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

class ReviewForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'class': 'w-full border rounded-md p-2'}), label='')

    class Meta:
        model = Review
        fields = ['content']

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'}))
    email_notifications = forms.BooleanField(required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    location = forms.CharField(max_length=100, required=False)
    website = forms.URLField(required=False)
    interests = forms.CharField(max_length=200, required=False, help_text='Enter your interests, separated by commas')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'userprofile'):
            profile = self.instance.userprofile
            self.fields['email_notifications'].initial = profile.email_notifications
            self.fields['profile_picture'].initial = profile.profile_picture
            self.fields['bio'].initial = profile.bio
            self.fields['location'].initial = profile.location
            self.fields['website'].initial = profile.website
            self.fields['interests'].initial = profile.interests

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            if self.cleaned_data.get('profile_picture'):
                profile.profile_picture = self.cleaned_data['profile_picture']
            profile.dark_mode = True  # Always keep dark mode enabled
            profile.email_notifications = self.cleaned_data.get('email_notifications', False)
            profile.bio = self.cleaned_data.get('bio', '')
            profile.location = self.cleaned_data.get('location', '')
            profile.website = self.cleaned_data.get('website', '')
            profile.interests = self.cleaned_data.get('interests', '')
            profile.save()
        return user

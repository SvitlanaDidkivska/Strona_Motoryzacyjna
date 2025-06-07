from django import forms
from tinymce.widgets import TinyMCE
from .models import ForumPost, ForumCategory, Comment

class ForumPostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCE(
            attrs={'cols': 80, 'rows': 30},
            mce_attrs={
                'menubar': False,
                'plugins': ['advlist autolink lists link image charmap print preview anchor',
                          'searchreplace visualblocks code fullscreen',
                          'insertdatetime media table paste code help wordcount mentions'],
                'toolbar': 'undo redo | formatselect | bold italic backcolor | \
                          alignleft aligncenter alignright alignjustify | \
                          bullist numlist outdent indent | removeformat | help'
            }
        )
    )
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
        })
    )

    class Meta:
        model = ForumPost
        fields = ['title', 'content', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Post title'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['category'].empty_label = "Select a category (optional)"

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCE(
            attrs={'cols': 80, 'rows': 10},
            mce_attrs={
                'menubar': False,
                'plugins': ['advlist autolink lists link image charmap preview',
                          'searchreplace visualblocks code',
                          'insertdatetime media table paste code help wordcount mentions image'],
                'toolbar': 'undo redo | formatselect | bold italic | \
                          alignleft aligncenter alignright alignjustify | \
                          bullist numlist | removeformat | help | image',
                'images_upload_url': '/forum/comment/image_upload/',
                'automatic_uploads': True,
                'images_upload_credentials': True,
            }
        )
    )

    class Meta:
        model = Comment
        fields = ['content']

class ForumCategoryForm(forms.ModelForm):
    class Meta:
        model = ForumCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Category description',
                'rows': 3
            })
        }

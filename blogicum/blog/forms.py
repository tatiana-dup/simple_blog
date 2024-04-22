from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.utils.timezone import get_current_timezone

from .models import Comment, Post


class ProfileEditForm(UserChangeForm):
    """Форма для изменения данных о пользователе, отображаемых в профиле."""

    class Meta:
        User = get_user_model()
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PostCreateForm(forms.ModelForm):
    """Форма для создания и редактирования поста."""
    
    class Meta:
        model = Post
        exclude = ('author', 'is_published')
        widgets = {'pub_date': forms.DateTimeInput(
            attrs={'type': 'datetime-local',
                   'timezone': get_current_timezone()},)}


class CommentCreateForm(forms.ModelForm):
    """Форма для создания и редактирования комментария."""

    class Meta:
        model = Comment
        fields = ('text', )

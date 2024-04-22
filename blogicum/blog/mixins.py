from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .models import Comment, Post


class PostAuthorRequiredMixin(UserPassesTestMixin):
    """
    Миксин проверяет, что текущий пользователь является автором поста.
    Если пользователь не автор, перенаправляет на страницу детального
    просмотра поста.
    """

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            Post.objects.select_related('author'),
            pk=kwargs['post_id']
        )
        if not self.test_func():
            return HttpResponseRedirect(reverse_lazy(
                'blog:post_detail',
                kwargs={'post_id': kwargs['post_id']}
            ))
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.object.author == self.request.user

    def get_object(self, queryset=None):
        return self.object

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)


class PostQuerySetMixin():
    """
    Миксин переопределяет метод get_queryset() для получения queryset постов
    с необходимыми связанными моделями, количеством комментариев и сортировкой.
    """

    def get_queryset(self):
        queryset = super().get_queryset(
        ).select_related(
            'author', 'category', 'location'
        ).annotate(
            comment_count=Count('comments')
        ).order_by(
            '-pub_date'
        )

        return queryset


class CommentMixin():
    """Миксимн с переопределенными методами для комментариев."""

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        if self.comment.author != request.user:
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.comment

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.comment.post_id})
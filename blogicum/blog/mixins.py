from django.shortcuts import get_object_or_404, redirect

from .models import Comment, Post


class PostAuthorRequiredMixin():
    """
    Миксин проверяет, что текущий пользователь является автором поста.
    Если пользователь не автор, перенаправляет на страницу детального
    просмотра поста.
    """

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        current_post = get_object_or_404(
            Post.objects.select_related('author'),
            pk=kwargs[self.pk_url_kwarg]
        )
        if not current_post.author == self.request.user:
            return redirect(current_post)
        return super().dispatch(request, *args, **kwargs)


class CommentMixin():
    """Миксимн с переопределенными методами для комментариев."""

    query_pk_and_slug = ('post_id', 'comment_id')
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return redirect(comment)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        post_id = self.kwargs.get(self.query_pk_and_slug[0])
        comment_id = self.kwargs.get(self.query_pk_and_slug[1])
        return get_object_or_404(
            Comment,
            id=comment_id,
            post=post_id)

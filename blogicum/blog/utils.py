from django.db.models import Count, Manager
from django.utils import timezone

from .models import Post


def get_queryset_posts(
        manager: Manager = Post.objects,
        add_annotate=True,
        add_filters=True):
    """Получает список постов по заданным параметрам."""
    posts = manager.select_related(
        'author',
        'category',
        'location'
    )
    if add_annotate:
        posts = posts.annotate(
            comment_count=Count('comments')
        ).order_by(
            '-pub_date'
        )

    if add_filters:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    return posts

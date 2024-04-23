from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Manager
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)

from blogicum.settings import POST_LIMIT_FOR_PAGINATE

from .forms import CommentCreateForm, PostCreateForm, ProfileEditForm
from .mixins import CommentMixin, PostAuthorRequiredMixin
from .models import Category, Comment, Post


def get_queryset_posts(
        manager: Manager = Post.objects,
        is_list_view=True,
        is_filtred=True):
    """Получает список постов по заданным параметрам."""
    current_time = timezone.now()
    posts = manager.select_related(
        'author',
        'category',
        'location'
    )
    if is_list_view:
        posts = posts.annotate(
            comment_count=Count('comments')
        ).order_by(
            '-pub_date'
        )

    if is_filtred:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=current_time,
            category__is_published=True
        )

    return posts


class PostListView(ListView):
    """
    Возвращает страницу с последними опубликованными постами
    в заданном количестве POST_LIMIT.
    """

    template_name = 'blog/index.html'
    paginate_by = POST_LIMIT_FOR_PAGINATE

    def get_queryset(self):
        return get_queryset_posts()


class PostDetailView(DetailView):
    """Возвращает страницу конкретного поста с комментариями."""

    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        current_post = get_object_or_404(
            Post,
            pk=self.kwargs[self.pk_url_kwarg]
        )
        current_time = timezone.now()

        if (self.request.user != current_post.author
            and (current_post.is_published is False
                 or current_post.pub_date > current_time
                 or current_post.category.is_published is False)):
            raise Http404

        return current_post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentCreateForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryPostsListView(ListView):
    """Возвращает страницу с постами в выбранной категории."""

    template_name = 'blog/category.html'
    paginate_by = POST_LIMIT_FOR_PAGINATE
    slug_url_kwarg = 'category_slug'

    # Андрей, если использовать функцию (если я все верно сделала, конечно),
    # то у меня дважды делается запрос к БД на получение объекта категории.
    # Именно поэтому я в первый раз решила использовать self.category
    # (то же самое про остальные классы, где я такое делала)
    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs[self.slug_url_kwarg],
            is_published=True,)

    def get_queryset(self):
        return get_queryset_posts(self.get_category().posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class ProfileListView(ListView):
    """
    Возвращает страницу с профилем пользователя, где указана краткая
    информация о нем и его посты.
    """

    template_name = 'blog/profile.html'
    paginate_by = POST_LIMIT_FOR_PAGINATE
    slug_url_kwarg = 'username'

    def get_author(self):
        return get_object_or_404(
            get_user_model(),
            username=self.kwargs[self.slug_url_kwarg])

    def get_queryset(self):
        author = self.get_author()

        if self.request.user == author:
            return get_queryset_posts(author.posts, is_filtred=False)
        else:
            return get_queryset_posts(author.posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Возвращяет страницу редактирования профиля пользователя."""

    model = get_user_model()
    form_class = ProfileEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})


class PostCreateView(LoginRequiredMixin, CreateView):
    """Возвращает страницу с формой для создания поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        local_time = form.cleaned_data['pub_date']
        utc_time = local_time.astimezone(timezone.utc)
        form.instance.pub_date = utc_time
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})


class PostUpdateView(PostAuthorRequiredMixin, UpdateView):
    """Возвращает страницу с формой для редактирования поста."""

    form_class = PostCreateForm


class PostDeleteView(PostAuthorRequiredMixin, DeleteView):
    """
    Возвращает страницу с информацией о посте
    для подтверждения его удаления.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostCreateForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Обрабатывает запрос на добавление нового комментария к посту."""

    model = Comment
    form_class = CommentCreateForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs[self.pk_url_kwarg])
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, UpdateView):
    """Обрабатывает запрос на редактирование комментария."""

    form_class = CommentCreateForm


class CommentDeleteView(CommentMixin, DeleteView):
    """
    Возвращает страницу с информацией о комментарии
    для подтверждения его удаления.
    """

    context_object_name = 'comment'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs[self.query_pk_and_slug[0]]}
        )


class UserCreateView(CreateView):
    """Возвращает страницу регистрации пользователя."""

    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')

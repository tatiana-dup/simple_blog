from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)

from .forms import CommentCreateForm, PostCreateForm, ProfileEditForm
from .mixins import CommentMixin, PostAuthorRequiredMixin, PostQuerySetMixin
from .models import Category, Comment, Post


# Количество постов для выдачи на странице.
POST_LIMIT = 10


class PostListView(PostQuerySetMixin, ListView):
    """
    Возвращает страницу с последними опубликованными постами
    в заданном количестве POST_LIMIT.
    """

    model = Post
    template_name = 'blog/index.html'
    paginate_by = POST_LIMIT

    def get_queryset(self):
        current_time = timezone.now()
        queryset = super().get_queryset(
        ).filter(
            is_published=True,
            pub_date__lte=current_time,
            category__is_published=True
        )
        return queryset


class PostDetailView(PostQuerySetMixin, DetailView):
    """Возвращает страницу конкретного поста с комментариями."""

    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        current_time = timezone.now()
        queryset = super().get_queryset()
        post = get_object_or_404(queryset, pk=self.kwargs['post_id'])

        if (self.request.user.is_authenticated
                and self.request.user == post.author):
            return queryset.filter(pk=post.pk)

        return queryset.filter(
            is_published=True,
            pub_date__lte=current_time,
            category__is_published=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentCreateForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryPostsListView(PostQuerySetMixin, ListView):
    """Возвращает страницу с постами в выбранной категории."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = POST_LIMIT

    def get_queryset(self):
        queryset = super().get_queryset()
        current_time = timezone.now()
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,)
        return queryset.filter(
            is_published=True,
            pub_date__lte=current_time,
            category__is_published=True,
            category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class ProfileListView(PostQuerySetMixin, ListView):
    """
    Возвращает страницу с профилем пользователя, где указана краткая
    информация о нем и его посты.
    """

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POST_LIMIT

    def get_queryset(self):
        queryset = super().get_queryset()
        self.author = get_object_or_404(
            get_user_model(),
            username=self.kwargs['username'])

        if (self.request.user.is_authenticated
                and self.request.user == self.author):
            return queryset.filter(author=self.author)
        else:
            current_time = timezone.now()
            return queryset.filter(
                is_published=True,
                pub_date__lte=current_time,
                category__is_published=True,
                author=self.author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Возвращяет страницу редактирования профиля пользователя."""

    model = get_user_model()
    form_class = ProfileEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        return get_object_or_404(get_user_model(), username=username)

    def test_func(self):
        return self.get_object() == self.request.user

    def get_success_url(self):
        return reverse_lazy(
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
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username})


class PostUpdateView(PostAuthorRequiredMixin, UpdateView):
    """Возвращает страницу с формой для редактирования поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(PostAuthorRequiredMixin, DeleteView):
    """
    Возвращает страницу с информацией о посте
    для подтверждения его удаления.
    """

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostCreateForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Обрабатывает запрос на добавление нового комментария к посту."""

    model = Comment
    form_class = CommentCreateForm

    def dispatch(self, request, *args, **kwargs):
        self.current_post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.current_post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.current_post.pk})


class CommentUpdateView(CommentMixin, UpdateView):
    """Обрабатывает запрос на редактирование комментария."""

    model = Comment
    query_pk_and_slug = ('post_id', 'comment_id')
    form_class = CommentCreateForm
    template_name = 'blog/comment.html'


class CommentDeleteView(CommentMixin, DeleteView):
    """
    Возвращает страницу с информацией о комментарии
    для подтверждения его удаления.
    """

    model = Comment
    query_pk_and_slug = ('post_id', 'comment_id')
    template_name = 'blog/comment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = self.comment
        return context

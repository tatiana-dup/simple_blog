from django.contrib.auth import get_user_model
from django.db import models


# Допустимая длина для полей-строк в моделях.
CHARFIELD_MAX_LENGTH = 256

# Длина строки для отображения в админ-панели.
LIMIT_STRING_DISPLAYED = 16

User = get_user_model()


class BaseModel(models.Model):
    """Абстрактная базовая модель, содержащая общие поля для всех моделей."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено')

    class Meta:
        abstract = True


class Category(BaseModel):
    """Модель для категорий постов."""

    title = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; разрешены символы '
                   'латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:LIMIT_STRING_DISPLAYED]


class Location(BaseModel):
    """Модель для местоположений, к которым могут быть привязаны посты."""

    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:LIMIT_STRING_DISPLAYED]


class Post(BaseModel):
    """Модель для постов блога."""

    title = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем — можно '
                   'делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации')
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория')
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='posts_images',
        blank=True,
        null=True,)

    class Meta:
        verbose_name = 'пост'
        verbose_name_plural = 'Посты'
        default_related_name = 'posts'

    def __str__(self):
        return self.title[:LIMIT_STRING_DISPLAYED]


class Comment(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено')
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('created_at',)

    def __str__(self):
        return (f'Комментарий от {self.author.username} '
                f'к посту {self.title[:LIMIT_STRING_DISPLAYED]}')

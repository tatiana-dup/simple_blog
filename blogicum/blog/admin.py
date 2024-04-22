from django.contrib import admin

from .models import Category, Location, Post


class PostAdmin(admin.ModelAdmin):
    """Класс с настройками страницы постов в админ-панели."""

    list_display = (
        'title',
        'is_published',
        'category',
        'location',
        'pub_date',
        'author')
    list_editable = ('is_published',)
    search_fields = ('title', 'pub_date')
    list_filter = (
        'is_published',
        'category',
        'location',
        'author')


class PostInline(admin.StackedInline):
    """Класс для вставки списка постов на страницы админ-панели."""

    model = Post
    extra = 0
    fields = ['title', 'is_published', 'text', 'pub_date']
    readonly_fields = ['title', 'text', 'pub_date']
    list_display_links = ('title',)


class CategoryAdmin(admin.ModelAdmin):
    """Класс с настройками страницы категорий в админ-панели."""

    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'is_published')
    list_editable = ('is_published',)
    search_fields = ('title',)
    list_filter = ('is_published',)


class LocationAdmin(admin.ModelAdmin):
    """Класс с настройками страницы местоположений в админ-панели."""

    inlines = (
        PostInline,
    )
    list_display = (
        'name',
        'is_published')
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)

admin.site.empty_value_display = 'Не задано'

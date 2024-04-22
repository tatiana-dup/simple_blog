from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    """Возвращает страницу с информацией о блоге."""

    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """Возвращает страницу с правилами блога."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Возвращает кастомную страницы при ошибке 404."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Возвращает кастомную страницы при ошибке 403 (проверка CSRF)."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Возвращает кастомную страницы при ошибке сервера 500."""
    return render(request, 'pages/500.html', status=500)

from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'


def hand404(request, exception):
    return render(request, 'pages/404.html', status=404)


def hand403(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def hand500(request):
    return render(request, 'pages/500.html', status=500)

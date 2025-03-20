from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.RulesPage.as_view(), name='about'),
    path('rules/', views.AboutPage.as_view(), name='rules'),
]

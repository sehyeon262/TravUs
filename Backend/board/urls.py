from django.urls import path
from . import views

urlpatterns = [
    path('blog', views.search_blog, name='search_blog'),
    path('news', views.search_news, name='search_news'),
    path('youtube', views.search_youtube, name='search_youtube'),
]

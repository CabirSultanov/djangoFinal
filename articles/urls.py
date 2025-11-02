from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed_all, name='feed_all'),
    path('popular/', views.feed_popular, name='feed_popular'),
    path('category/<slug:slug>/', views.feed_by_category, name='feed_by_category'),

    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('article/create/', views.article_create, name='article_create'),
    path('article/<int:pk>/edit/', views.article_update, name='article_update'),
    path('article/<int:pk>/delete/', views.article_delete, name='article_delete'),

    path('article/<int:pk>/like/', views.article_like, name='article_like'),
    path('article/<int:pk>/dislike/', views.article_dislike, name='article_dislike'),
    path('article/<int:pk>/bookmark/', views.article_bookmark_toggle, name='article_bookmark'),
    path('article/<int:pk>/rate/<int:value>/', views.article_rate, name='article_rate'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed_all, name='feed_all'),
    path('popular/', views.feed_popular, name='feed_popular'),
    path('category/<slug:slug>/', views.feed_by_category, name='feed_by_category'),
    path('authors/', views.feed_authors, name='feed_authors'),
    path('favorites/', views.feed_favorites, name='feed_favorites'),
    path('my/', views.feed_my_articles, name='feed_my_articles'),

    path('moderation/', views.moderation_queue, name='moderation_queue'),
    path('moderation/<int:pk>/approve/', views.moderation_approve, name='moderation_approve'),

    path('create/', views.article_create, name='article_create'),
    path('<int:pk>/', views.article_detail, name='article_detail'),
    path('<int:pk>/edit/', views.article_update, name='article_update'),
    path('<int:pk>/delete/', views.article_delete, name='article_delete'),

    path('<int:pk>/like/', views.article_like, name='article_like'),
    path('<int:pk>/dislike/', views.article_dislike, name='article_dislike'),
    path('<int:pk>/bookmark/', views.article_bookmark_toggle, name='article_bookmark_toggle'),
    path('<int:pk>/rate/<int:value>/', views.article_rate, name='article_rate'),
    path('<int:pk>/confirm/', views.article_confirm, name='article_confirm'),
path('articles/<int:pk>/edit/', views.article_update, name='article_update'),


]

from django.contrib import admin
from .models import Category, Article, Rating, LikeDislike, Bookmark

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'rating', 'created_at')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'content')

admin.site.register(Rating)
admin.site.register(LikeDislike)
admin.site.register(Bookmark)

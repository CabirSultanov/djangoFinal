from django.contrib import admin, messages
from django.contrib.auth.models import Group  # ← чтобы скрыть Groups
from .models import Category, Article


# ✅ Убираем стандартную модель Groups из админки
admin.site.unregister(Group)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'rating', 'created_at')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)

    # ✅ Экшены для модерации
    actions = ['approve_articles', 'unpublish_articles']

    @admin.action(description="✅ Approve selected articles (publish)")
    def approve_articles(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} article(s) approved successfully!", messages.SUCCESS)

    @admin.action(description="🚫 Unpublish selected articles")
    def unpublish_articles(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} article(s) unpublished.", messages.WARNING)

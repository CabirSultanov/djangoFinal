from django.contrib import admin, messages
from django.contrib.auth.models import Group
from .models import Category, Article

admin.site.unregister(Group)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'rating_percent_display', 'created_at')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)

    actions = ['approve_articles', 'unpublish_articles']


    @admin.display(description="Like Rating %")
    def rating_percent_display(self, obj):
        likes = obj.votes.filter(value=1).count()
        dislikes = obj.votes.filter(value=-1).count()
        total = likes + dislikes
        if total == 0:
            return "0%"
        return f"{round((likes / total) * 100, 1)}%"

    @admin.action(description="✅ Approve selected articles (publish)")
    def approve_articles(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} article(s) approved successfully!", messages.SUCCESS)

    @admin.action(description="🚫 Unpublish selected articles")
    def unpublish_articles(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} article(s) unpublished.", messages.WARNING)

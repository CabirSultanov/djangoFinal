from django.apps import AppConfig

DEFAULT_CATEGORIES = [
    ('Backend', 'backend'),
    ('Frontend', 'frontend'),
    ('AI', 'ai'),
    ('Cyber Security', 'cyber-security'),
    ('Cyber Sport', 'cyber-sport'),
    ('Game Development', 'game-dev'),
]

class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articles'

    def ready(self):
        from django.db.models.signals import post_migrate
        from .models import Category

        def seed_categories(sender, **kwargs):
            for name, slug in DEFAULT_CATEGORIES:
                Category.objects.get_or_create(slug=slug, defaults={'name': name})

        post_migrate.connect(seed_categories, sender=self)

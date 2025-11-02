from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # колонки, которые видны в списке пользователей
    list_display = ('username', 'email', 'display_role')
    list_filter = ('role',)
    search_fields = ('username', 'email')
    ordering = ('username',)

    # форма редактирования
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('role',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

    actions = ['promote_to_admin', 'demote_to_user']

    # показываем "Super Admin" для суперпользователей
    def display_role(self, obj):
        if obj.is_superuser:
            return "Super Admin"
        return obj.get_role_display()
    display_role.short_description = "Role"

    @admin.action(description="Promote selected users to Admin")
    def promote_to_admin(self, request, queryset):
        updated = queryset.update(role=User.Roles.ADMIN, is_staff=True)
        self.message_user(request, f"{updated} user(s) promoted to Admin.", messages.SUCCESS)

    @admin.action(description="Demote selected users to User")
    def demote_to_user(self, request, queryset):
        updated = queryset.update(role=User.Roles.USER, is_staff=False)
        self.message_user(request, f"{updated} user(s) demoted to User.", messages.INFO)

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # убрал 'is_superuser' 👇
    list_display = ('username', 'email', 'role', 'is_banned', 'is_staff')
    list_filter = ('role', 'is_banned', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'is_banned')}),
    )

    actions = ['promote_to_admin', 'demote_to_user', 'ban_selected_users', 'unban_selected_users']

    @admin.action(description="Promote selected users to Admin")
    def promote_to_admin(self, request, queryset):
        updated = queryset.update(role=User.Roles.ADMIN, is_staff=True)
        self.message_user(request, f"{updated} user(s) promoted to Admin.", messages.SUCCESS)

    @admin.action(description="Demote selected users to User")
    def demote_to_user(self, request, queryset):
        updated = queryset.update(role=User.Roles.USER, is_staff=False)
        self.message_user(request, f"{updated} user(s) demoted to User.", messages.INFO)

    @admin.action(description="Ban selected users")
    def ban_selected_users(self, request, queryset):
        updated = queryset.update(is_banned=True)
        self.message_user(request, f"{updated} user(s) banned.", messages.WARNING)

    @admin.action(description="Unban selected users")
    def unban_selected_users(self, request, queryset):
        updated = queryset.update(is_banned=False)
        self.message_user(request, f"{updated} user(s) unbanned.", messages.SUCCESS)

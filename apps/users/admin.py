from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserProfile, FeishuIdentity


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'department', 'position', 'is_active', 'date_joined']
    list_filter = ['is_active', 'department', 'position']
    search_fields = ['username', 'email', 'first_name', 'last_name']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'language', 'timezone']


@admin.register(FeishuIdentity)
class FeishuIdentityAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'app_id', 'open_id', 'tenant_key']
    search_fields = ['user__username', 'display_name', 'open_id', 'tenant_key']
    autocomplete_fields = ['user']
    readonly_fields = ['created_at']

"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'username', 'is_active',
        'is_staff', 'is_verified', 'is_superuser'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_verified', 'is_superuser'
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

    fieldsets = (
        (_('Authentication'), {
            'fields': ('email', 'username', 'password')
        }),
        (_('Permissions'), {
            'fields': (
                'is_staff', 'is_active', 'is_verified', 'is_superuser'
            )
        }),
        (_('Group Permissions'), {
            'fields': ('groups', 'user_permissions')
        }),
        (_('Important Date'), {
            'fields': ('last_login',)
        }),
    )
    readonly_fields = ('last_login',)

    add_fieldsets = (
        ('Authentication', {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2'
            ),
        }),
        ('Permissions', {
            'fields': (
                'is_staff', 'is_active', 'is_verified', 'is_superuser'
            )
        }),
    )

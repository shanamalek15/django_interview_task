from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_superuser', 'is_active')
    list_filter = ('is_active', 'role', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role', 'is_active', 'is_superuser')}),
        ('Permissions', {'fields': ('user_permissions',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
    search_fields = ('email',)
    ordering = ('-date_joined',)
        
# admin.site.register(User)
admin.site.register(User, UserAdmin)
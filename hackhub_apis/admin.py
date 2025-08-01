from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email','username','full_name','is_staff')
    list_filter = ('is_staff','is_superuser')
    fieldsets = (
        (None, {'fields': ('email','username','password')}),
        ('Personal Info', {'fields': ('full_name')}),
        ('Permissions',{'fields':('is_staff','is_superuser','is_active','groups','user_permissions')})
    )

    add_fieldsets = (
        (None,{
            'fields':('email','username','full_name','password1','password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('id')

admin.site.register(CustomUser,CustomUserAdmin)
# Register your models here.

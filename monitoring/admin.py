from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Device, DeviceReading, HealthRecord


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('kode_perangkat', 'nama_perangkat', 'user', 'last_seen', 'created_at')
    search_fields = ('kode_perangkat', 'nama_perangkat', 'user__username')


@admin.register(DeviceReading)
class DeviceReadingAdmin(admin.ModelAdmin):
    list_display = ('device', 'last_reading_time', 'is_valid', 'updated_at')


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('device', 'timestamp', 'heart_rate_bpm','heart_status','body_temp_c','temp_status', 'overall_status')
    list_filter = ('overall_status',)


# Customize User Admin - Remove first name & last name columns
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Remove first_name & last_name from list display
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    
    # Remove first_name & last_name from fieldsets (edit form)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informasi Pribadi', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Remove first_name & last_name from add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

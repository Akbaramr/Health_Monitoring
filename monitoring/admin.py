from django.contrib import admin
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
    list_display = ('device', 'timestamp', 'heart_rate_bpm', 'body_temp_c', 'overall_status')
    list_filter = ('overall_status',)

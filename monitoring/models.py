from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    kode_perangkat = models.CharField(max_length=100, unique=True)
    nama_perangkat = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_perangkat or self.kode_perangkat

    def display_name(self):
        return self.nama_perangkat or self.kode_perangkat


class DeviceReading(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='reading')
    last_heart_rate_bpm = models.FloatField(null=True, blank=True)
    last_body_temp_c = models.FloatField(null=True, blank=True)
    last_reading_time = models.DateTimeField(null=True, blank=True)
    heart_status = models.CharField(max_length=20, blank=True)
    temp_status = models.CharField(max_length=20, blank=True)
    overall_status = models.CharField(max_length=10, blank=True)
    is_valid = models.BooleanField(default=False)
    last_saved_reading_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Reading {self.device.display_name()}'


class HealthRecord(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='records')
    timestamp = models.DateTimeField(default=timezone.now)
    heart_rate_bpm = models.FloatField()
    body_temp_c = models.FloatField()
    heart_status = models.CharField(max_length=20)
    temp_status = models.CharField(max_length=20)
    overall_status = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.device.display_name()} @ {self.timestamp}'

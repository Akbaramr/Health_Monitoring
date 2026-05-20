import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_monitoring.settings')
django.setup()

from monitoring.models import Device, DeviceReading

print("=== DAFTAR PERANGKAT ===")
devices = Device.objects.all()
for d in devices:
    print(f"\nDevice: {d.display_name()}")
    print(f"  Kode: {d.kode_perangkat}")
    print(f"  User: {d.user.username}")
    print(f"  Last Seen: {d.last_seen}")
    
    reading = DeviceReading.objects.filter(device=d).first()
    if reading:
        print(f"  Last BPM: {reading.last_heart_rate_bpm}")
        print(f"  Last Temp: {reading.last_body_temp_c}")
    else:
        print(f"  No readings yet")

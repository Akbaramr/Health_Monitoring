import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_monitoring.settings')
django.setup()

from django.contrib.auth.models import User
users = User.objects.all()
print("Total users:", users.count())
for u in users:
    print(f"  - {u.username} ({u.email})")

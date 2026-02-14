from .models import Device
from .utils import connection_status


def active_device(request):
    device = None
    connection = None
    device_id = request.session.get('active_device_id')
    if request.user.is_authenticated and device_id:
        device = Device.objects.filter(id=device_id, user=request.user).first()
        if not device:
            request.session.pop('active_device_id', None)
        else:
            connection = connection_status(device.last_seen)
    return {'active_device': device, 'active_device_connection': connection}

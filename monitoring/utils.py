from django.utils import timezone


def classify_heart_status(bpm):
    if bpm is None:
        return ''
    if bpm < 60:
        return 'Bradykardia'
    if bpm <= 100:
        return 'Normal'
    return 'Takikardia'


def classify_temp_status(temp_c):
    if temp_c is None:
        return ''
    if temp_c < 36.0:
        return 'Hipotermia'
    if temp_c <= 37.5:
        return 'Normal'
    if temp_c <= 40.0:
        return 'Pireksia'
    return 'Hipertermia'


def classify_overall_status(heart_status, temp_status):
    heart_normal = heart_status == 'Normal'
    temp_normal = temp_status == 'Normal'
    
    if heart_normal and temp_normal:
        return 'Sehat'
    elif not heart_normal and not temp_normal:
        return 'Bahaya'
    else:
        return 'Waspada'


def is_reading_valid(bpm, temp_c):
    if bpm is None or temp_c is None:
        return False
    if bpm <= 0:
        return False
    if bpm < 30 or bpm > 220:
        return False
    if temp_c < 30.0 or temp_c > 45.0:
        return False
    return True


def connection_status(last_seen, threshold_seconds=30):
    if not last_seen:
        return 'disconnected'
    now = timezone.now()
    delta = now - last_seen
    if delta.total_seconds() <= threshold_seconds:
        return 'connected'
    return 'disconnected'

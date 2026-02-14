import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt

from .forms import DeviceAddForm, SignUpForm
from .models import Device, DeviceReading, HealthRecord
from .utils import (
    classify_heart_status,
    classify_temp_status,
    classify_overall_status,
    connection_status,
    is_reading_valid,
)


def get_active_device(request):
    device_id = request.session.get('active_device_id')
    if not device_id:
        return None
    device = Device.objects.filter(id=device_id, user=request.user).first()
    if not device:
        request.session.pop('active_device_id', None)
    return device


@login_required
def device_select(request):
    devices = Device.objects.filter(user=request.user).order_by('id')

    if request.method == 'POST':
        device_id = request.POST.get('device_id')
        device = devices.filter(id=device_id).first()
        if device:
            request.session['active_device_id'] = device.id
            return redirect('dashboard')

    return render(request, 'monitoring/device_select.html', {'devices': devices})


@login_required
def device_add(request):
    if request.method == 'POST':
        form = DeviceAddForm(request.POST)
        if form.is_valid():
            kode = form.cleaned_data['kode_perangkat']
            nama = form.cleaned_data.get('nama_perangkat', '')
            existing = Device.objects.filter(kode_perangkat=kode).first()
            if existing:
                if existing.user == request.user:
                    messages.warning(request, 'Perangkat sudah terdaftar pada akun Anda.')
                else:
                    messages.error(request, 'Kode perangkat sudah digunakan user lain.')
            else:
                device = Device.objects.create(
                    user=request.user,
                    kode_perangkat=kode,
                    nama_perangkat=nama,
                )
                request.session['active_device_id'] = device.id
                messages.success(request, 'Perangkat berhasil ditambahkan.')
                return redirect('dashboard')
    else:
        form = DeviceAddForm()

    return render(request, 'monitoring/device_add.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'monitoring/dashboard.html')


@login_required
def grafik(request):
    return render(request, 'monitoring/grafik.html')


@login_required
def histori(request):
    device = get_active_device(request)
    
    if device:
        records = HealthRecord.objects.filter(device=device).order_by('-timestamp')

        from_date = request.GET.get('from', '')
        to_date = request.GET.get('to', '')

        if from_date:
            records = records.filter(timestamp__date__gte=from_date)
        if to_date:
            records = records.filter(timestamp__date__lte=to_date)

        paginator = Paginator(records, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        query_params = ''
        if from_date:
            query_params += f'&from={from_date}'
        if to_date:
            query_params += f'&to={to_date}'

        context = {
            'page_obj': page_obj,
            'from_date': from_date,
            'to_date': to_date,
            'query_params': query_params,
        }
    else:
        context = {
            'page_obj': None,
            'from_date': '',
            'to_date': '',
            'query_params': '',
        }
    
    return render(request, 'monitoring/histori.html', context)


def _to_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_timestamp(value):
    if not value:
        return timezone.now()
    parsed = parse_datetime(value)
    if not parsed:
        return timezone.now()
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


@csrf_exempt
def api_iot_ingest(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'method_not_allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid_json'}, status=400)

    kode = payload.get('kode_perangkat')
    if not kode:
        return JsonResponse({'error': 'missing_kode_perangkat'}, status=400)

    device = Device.objects.filter(kode_perangkat=kode).first()
    if not device:
        return JsonResponse({'error': 'device_not_found'}, status=404)

    bpm = _to_float(payload.get('heart_rate_bpm'))
    temp_c = _to_float(payload.get('body_temp_c'))
    reading_time = _parse_timestamp(payload.get('timestamp'))

    heart_status = classify_heart_status(bpm)
    temp_status = classify_temp_status(temp_c)
    overall_status = classify_overall_status(heart_status, temp_status)
    valid = is_reading_valid(bpm, temp_c)

    reading, _ = DeviceReading.objects.get_or_create(device=device)
    reading.last_heart_rate_bpm = bpm
    reading.last_body_temp_c = temp_c
    reading.last_reading_time = reading_time
    reading.heart_status = heart_status
    reading.temp_status = temp_status
    reading.overall_status = overall_status
    reading.is_valid = valid
    reading.save()

    device.last_seen = timezone.now()
    device.save(update_fields=['last_seen'])

    return JsonResponse({'status': 'ok'})


@login_required
def api_latest(request):
    device = get_active_device(request)
    if not device:
        return JsonResponse({'error': 'no_active_device'}, status=400)

    reading = DeviceReading.objects.filter(device=device).first()
    if not reading:
        return JsonResponse({
            'kode_perangkat': device.kode_perangkat,
            'nama_perangkat': device.display_name(),
            'last_reading_time': None,
            'heart_rate_bpm': None,
            'body_temp_c': None,
            'heart_status': None,
            'temp_status': None,
            'overall_status': None,
            'connection': connection_status(device.last_seen),
            'last_seen': device.last_seen.isoformat() if device.last_seen else None,
            'is_valid': False,
            'can_save': False,
        })

    can_save = (
        reading.is_valid
        and reading.last_reading_time
        and reading.last_reading_time != reading.last_saved_reading_time
    )

    return JsonResponse({
        'kode_perangkat': device.kode_perangkat,
        'nama_perangkat': device.display_name(),
        'last_reading_time': reading.last_reading_time.isoformat() if reading.last_reading_time else None,
        'heart_rate_bpm': reading.last_heart_rate_bpm,
        'body_temp_c': reading.last_body_temp_c,
        'heart_status': reading.heart_status,
        'temp_status': reading.temp_status,
        'overall_status': reading.overall_status,
        'connection': connection_status(device.last_seen),
        'last_seen': device.last_seen.isoformat() if device.last_seen else None,
        'is_valid': reading.is_valid,
        'can_save': can_save,
    })


@login_required
def api_save_latest(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'method_not_allowed'}, status=405)

    device = get_active_device(request)
    if not device:
        return JsonResponse({'error': 'no_active_device'}, status=400)

    reading = DeviceReading.objects.filter(device=device).first()
    if not reading or not reading.is_valid or not reading.last_reading_time:
        return JsonResponse({'error': 'no_valid_reading'}, status=400)

    if reading.last_saved_reading_time == reading.last_reading_time:
        return JsonResponse({'status': 'already_saved'})

    HealthRecord.objects.create(
        device=device,
        timestamp=reading.last_reading_time,
        heart_rate_bpm=reading.last_heart_rate_bpm,
        body_temp_c=reading.last_body_temp_c,
        heart_status=reading.heart_status,
        temp_status=reading.temp_status,
        overall_status=reading.overall_status,
    )

    reading.last_saved_reading_time = reading.last_reading_time
    reading.save(update_fields=['last_saved_reading_time'])

    return JsonResponse({'status': 'ok'})


@login_required
def api_records(request):
    device = get_active_device(request)
    if not device:
        return JsonResponse({'error': 'no_active_device'}, status=400)

    try:
        limit = int(request.GET.get('limit', 20))
    except ValueError:
        limit = 20

    records = list(
        HealthRecord.objects.filter(device=device)
        .order_by('-timestamp')[:limit]
    )
    records.reverse()

    data = []
    for record in records:
        data.append({
            'timestamp': record.timestamp.isoformat(),
            'timestamp_label': record.timestamp.strftime('%H:%M:%S'),
            'heart_rate_bpm': record.heart_rate_bpm,
            'body_temp_c': record.body_temp_c,
        })

    return JsonResponse({'records': data})


def custom_logout(request):
    logout(request)
    return redirect('login')


@login_required
def api_devices_list(request):
    devices = Device.objects.filter(user=request.user).order_by('-created_at')
    devices_data = []
    for device in devices:
        devices_data.append({
            'id': device.id,
            'kode_perangkat': device.kode_perangkat,
            'nama_perangkat': device.nama_perangkat,
            'is_active': request.session.get('active_device_id') == device.id,
            'last_seen': device.last_seen.isoformat() if device.last_seen else None,
        })
    return JsonResponse({'devices': devices_data})


@login_required
def api_device_set_active(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        device_id = data.get('device_id')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    if not device_id:
        return JsonResponse({'success': False, 'message': 'Device ID is required'}, status=400)

    device = Device.objects.filter(id=device_id, user=request.user).first()
    if not device:
        return JsonResponse({'success': False, 'message': 'Device not found'}, status=404)

    request.session['active_device_id'] = device.id
    return JsonResponse({'success': True, 'message': 'Device set as active successfully'})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('login')  # Arahkan ke halaman login setelah registrasi
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

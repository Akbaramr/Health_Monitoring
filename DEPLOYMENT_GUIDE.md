# 🚀 Panduan Deployment Production - Health Monitoring

**Server:** Jetorbit VPS (103.235.75.208)  
**Tanggal:** 4 Maret 2026

---

## ✅ Status Saat Ini

- [x] Gunicorn sudah running
- [x] Website bisa diakses (masih development mode)
- [x] API endpoint ESP32 tersedia

---

## ⏳ Yang Harus Dilakukan

### Step 1: Buka Firewall di Jetorbit

**PENTING:** Port 8000 harus dibuka agar bisa diakses dari internet!

1. Login ke dashboard Jetorbit: https://jetorbit.com
2. Klik **Manage** pada server `health-monitoring`
3. Cari menu **Firewall** atau **Security Groups**
4. Tambahkan rule baru:
   - **Port:** 8000
   - **Protocol:** TCP
   - **Source:** 0.0.0.0/0 (allow all)
5. Save

**Atau via SSH (jika firewall Ubuntu):**
```bash
# Cek status firewall
sudo ufw status

# Jika inactive, aktifkan dan buka port
sudo ufw allow 8000/tcp
sudo ufw enable

# Atau jika sudah active, cukup tambahkan rule
sudo ufw allow 8000/tcp
```

---

### Step 2: Stop Gunicorn yang Sedang Jalan

Di PuTTY, tekan `Ctrl+C` untuk stop Gunicorn yang sedang running.

---

### Step 3: Collect Static Files

```bash
cd ~/Health_Monitoring
source venv/bin/activate
python manage.py collectstatic --noinput
```

---

### Step 4: Buat Systemd Service

Ini agar Gunicorn otomatis jalan saat server restart.

```bash
sudo nano /etc/systemd/system/gunicorn-health.service
```

Paste konfigurasi berikut:

```ini
[Unit]
Description=Gunicorn Health Monitoring Service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/Health_Monitoring
ExecStart=/root/venv/bin/gunicorn health_monitoring.wsgi:application --bind 0.0.0.0:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Simpan dengan `Ctrl+O`, `Enter`, lalu `Ctrl+X`.

---

### Step 5: Enable dan Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable gunicorn-health

# Start service
sudo systemctl start gunicorn-health

# Cek status
sudo systemctl status gunicorn-health
```

Harusnya muncul status `active (running)`.

---

### Step 6: Test Akses dari Browser

Buka browser dan akses:
- **Homepage:** http://103.235.75.208:8000/
- **Admin:** http://103.235.75.208:8000/admin/

Login dengan:
- **Username:** admin
- **Password:** (password yang Anda set saat createsuperuser)

---

### Step 7: Setup ESP32

**Endpoint API untuk ESP32:**

```
POST http://103.235.75.208:8000/api/iot/ingest/
Content-Type: application/json
```

**Format JSON:**
```json
{
  "kode_perangkat": "DEVICE001",
  "heart_rate_bpm": 75.5,
  "body_temp_c": 36.5,
  "timestamp": "2026-03-04T14:30:00",
  "finger_detected": true,
  "bpm_frozen": false
}
```

**Contoh Code ESP32 (Arduino):**

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://103.235.75.208:8000/api/iot/ingest/";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    // Ganti dengan data sensor Anda
    String jsonPayload = "{\"kode_perangkat\":\"DEVICE001\",\"heart_rate_bpm\":75.5,\"body_temp_c\":36.5,\"finger_detected\":true,\"bpm_frozen\":false}";
    
    int httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.println("Error sending data");
    }
    
    http.end();
  }
  
  delay(5000); // Kirim setiap 5 detik
}
```

---

## 🔧 Perintah Berguna

```bash
# Cek status Gunicorn
sudo systemctl status gunicorn-health

# Restart Gunicorn
sudo systemctl restart gunicorn-health

# Stop Gunicorn
sudo systemctl stop gunicorn-health

# Lihat log Gunicorn
sudo journalctl -u gunicorn-health -f

# Cek apakah port 8000 listening
sudo netstat -tulpn | grep 8000
```

---

## 🎯 Checklist Final

```
[ ] Firewall dibuka (port 8000)
[ ] Gunicorn systemd service dibuat
[ ] Service running (systemctl status)
[ ] Website bisa diakses dari browser
[ ] Admin bisa login
[ ] ESP32 bisa kirim data
[ ] Data muncul di dashboard
```

---

## 🆘 Troubleshooting

### Website tidak bisa diakses
```bash
# Cek firewall
sudo ufw status

# Cek Gunicorn running
sudo systemctl status gunicorn-health

# Cek port listening
sudo netstat -tulpn | grep 8000
```

### ESP32 gagal kirim data
1. Pastikan WiFi ESP32 terhubung
2. Cek IP server di code ESP32 (harus 103.235.75.208)
3. Pastikan port 8000 tidak diblok firewall
4. Test dengan Postman/curl dulu:
   ```bash
   curl -X POST http://103.235.75.208:8000/api/iot/ingest/ \
     -H "Content-Type: application/json" \
     -d '{"kode_perangkat":"DEVICE001","heart_rate_bpm":75.5,"body_temp_c":36.5}'
   ```

---

**Good luck! 🚀**

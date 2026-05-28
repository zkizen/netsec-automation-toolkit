import requests
import time
from datetime import datetime

# Konfigurasi Telegram
TELEGRAM_TOKEN = "8871724584:AAEvTYKSiwgMc6mzTgPUelmGEDmuvPoexjg"
TELEGRAM_CHAT_ID = "6208876002"

# Threshold anomali (dalam ms)
PING_THRESHOLD = 200  # alert kalau latency > 200ms
DOWN_THRESHOLD = 3    # alert kalau gagal ping 3x berturut-turut

HOSTS = {
    "R1": "192.168.12.1",
    "R2": "192.168.12.2",
    "R3": "192.168.23.2",
    "Google DNS": "8.8.8.8",
}

fail_count = {host: 0 for host in HOSTS}

def send_telegram(message):
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def ping(host):
    import subprocess
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", host],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def monitor():
    print("🔍 NetSec Anomaly Detector started...")
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] Checking hosts...")
        for name, ip in HOSTS.items():
            status = ping(ip)
            if not status:
                fail_count[name] += 1
                print(f"  ⚠️  {name} ({ip}) - DOWN [{fail_count[name]}x]")
                if fail_count[name] == DOWN_THRESHOLD:
                    msg = f"🚨 ALERT [{timestamp}]\n{name} ({ip}) DOWN {DOWN_THRESHOLD}x berturut-turut!"
                    send_telegram(msg)
            else:
                if fail_count[name] >= DOWN_THRESHOLD:
                    msg = f"✅ RECOVERED [{timestamp}]\n{name} ({ip}) kembali UP!"
                    send_telegram(msg)
                fail_count[name] = 0
                print(f"  ✅ {name} ({ip}) - UP")
        print(f"  Cek ulang dalam 30 detik...")
        time.sleep(30)

if __name__ == "__main__":
    monitor()

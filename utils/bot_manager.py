from __future__ import annotations
import subprocess
import sys
import os
import signal

BOT_PROCESS = None
BOT_PID_FILE = "bot_pid.txt"

def _get_bot_pid() -> int | None:
    """Bot PID'sini dosyadan okur."""
    if os.path.exists(BOT_PID_FILE):
        with open(BOT_PID_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return None
    return None

def _save_bot_pid(pid: int) -> None:
    """Bot PID'sini dosyaya yazar."""
    with open(BOT_PID_FILE, "w") as f:
        f.write(str(pid))

def _delete_bot_pid_file() -> None:
    """Bot PID dosyasını siler."""
    if os.path.exists(BOT_PID_FILE):
        os.remove(BOT_PID_FILE)

def start_bot() -> dict:
    """Botu ayrı bir süreçte başlatır."""
    global BOT_PROCESS
    current_status = get_bot_status()
    if current_status["status"] == "running":
        return {"status": "error", "message": "Bot zaten çalışıyor."}
    
    # Eğer PID dosyası varsa ama süreç çalışmıyorsa, PID dosyasını temizle
    if _get_bot_pid():
        _delete_bot_pid_file()

    try:
        # main.py'yi ayrı bir süreçte başlat
        # Detached modda çalıştırmak için platforma özel ayarlamalar gerekebilir.
        # Windows için CREATE_NEW_PROCESS_GROUP kullanıyoruz.
        # Linux/macOS için preexec_fn=os.setsid kullanılabilir.
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        BOT_PROCESS = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            creationflags=creationflags
        )
        _save_bot_pid(BOT_PROCESS.pid)
        return {"status": "success", "message": f"Bot başlatıldı. PID: {BOT_PROCESS.pid}"}
    except Exception as e:
        return {"status": "error", "message": f"Bot başlatılırken hata oluştu: {e}"}

def stop_bot() -> dict:
    """Çalışan bot sürecini durdurur."""
    pid = _get_bot_pid()
    if not pid:
        return {"status": "error", "message": "Bot çalışmıyor."}

    try:
        if sys.platform == "win32":
            # Windows'ta süreç grubunu sonlandırmak için taskkill kullanıyoruz
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], check=True)
        else:
            # Unix benzeri sistemlerde süreç grubuna SIGTERM gönderiyoruz
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        _delete_bot_pid_file()
        return {"status": "success", "message": f"Bot durduruldu. PID: {pid}"}
    except Exception as e:
        return {"status": "error", "message": f"Bot durdurulurken hata oluştu: {e}"}

def restart_bot() -> dict:
    """Botu yeniden başlatır."""
    stop_result = stop_bot()
    if stop_result["status"] == "error" and "Bot çalışmıyor" not in stop_result["message"]:
        return stop_result # Durdurma işleminde beklenmedik bir hata oluştuysa

    start_result = start_bot()
    return start_result

def get_bot_status() -> dict:
    """Botun çalışma durumunu kontrol eder."""
    pid = _get_bot_pid()
    if pid:
        try:
            # Sürecin hala çalışıp çalışmadığını kontrol et
            if sys.platform == "win32":
                # Windows'ta tasklist ile PID kontrolü
                result = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True, check=True)
                if str(pid) in result.stdout:
                    return {"status": "running", "pid": pid}
            else:
                # Unix benzeri sistemlerde kill -0 ile kontrol
                os.kill(pid, 0)
                return {"status": "running", "pid": pid}
        except (ProcessLookupError, OSError, subprocess.CalledProcessError):
            _delete_bot_pid_file() # PID dosyası var ama süreç yoksa sil
            return {"status": "stopped", "message": "Bot çalışmıyor (PID dosyası temizlendi)."}
    return {"status": "stopped", "message": "Bot çalışmıyor."}

if __name__ == "__main__":
    # Test amaçlı kullanım
    status = get_bot_status()
    print(f"Başlangıç durumu: {status}")

    if status["status"] == "stopped":
        print("Bot başlatılıyor...")
        result = start_bot()
        print(result)
        import time
        time.sleep(5) # Botun başlaması için biraz bekle
        print(f"Yeni durum: {get_bot_status()}")
        print("Bot durduruluyor...")
        print(stop_bot())
        print(f"Son durum: {get_bot_status()}")
    else:
        print("Bot zaten çalışıyor, durduruluyor...")
        print(stop_bot())
        print(f"Son durum: {get_bot_status()}")

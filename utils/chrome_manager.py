"""
Chrome Manager - Chrome for Testing yönetimi
"""

import os
import subprocess
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ChromeManager:
    def __init__(self):
        self.chrome_dir = Path("chrome_for_testing")
        self.chrome_exe = None
        self.find_chrome_executable()
    
    def find_chrome_executable(self):
        """Chrome executable'ını bul"""
        possible_paths = [
            Path(r"C:/Program Files/Google/Chrome/Application/chrome.exe"),
            Path(r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
            self.chrome_dir / "chrome-win64" / "chrome.exe",
            self.chrome_dir / "chrome-win32" / "chrome.exe",
        ]
        # Chrome klasörlerini ara
        for chrome_dir in self.chrome_dir.glob("chrome-*"):
            possible_paths.append(chrome_dir / "chrome.exe")
        for path in possible_paths:
            if path.exists():
                self.chrome_exe = path
                logger.info(f"Chrome executable bulundu: {self.chrome_exe}")
                return
        logger.warning("Chrome executable bulunamadı!")
        self.chrome_exe = None
    
    def is_chrome_installed(self):
        """Chrome kurulu mu kontrol et"""
        return self.chrome_exe is not None and self.chrome_exe.exists()
    
    def get_chrome_version(self):
        """Chrome versiyonunu al"""
        if not self.is_chrome_installed():
            return None
        
        try:
            result = subprocess.run(
                [str(self.chrome_exe), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.error(f"Chrome versiyonu alınamadı: {e}")
        
        return None
    
    def launch_chrome_app(self, url, app_mode=True, maximized=True):
        """Chrome'u app modunda başlat"""
        if not self.is_chrome_installed():
            logger.error("Chrome kurulu değil!")
            return False
        
        try:
            cmd = [str(self.chrome_exe)]
            
            if app_mode:
                cmd.extend(["--app", url])
            else:
                cmd.append(url)
            
            if maximized:
                cmd.append("--start-maximized")
            
            # Güvenlik ve performans ayarları
            cmd.extend([
                "--disable-features=RendererCodeIntegrity",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-notifications"
            ])
            
            logger.info(f"Chrome başlatılıyor: {' '.join(cmd)}")
            
            # Chrome'u başlat
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            logger.info(f"Chrome başlatıldı (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Chrome başlatılamadı: {e}")
            return False
    
    def install_chrome_if_needed(self):
        """Chrome kurulu değilse kur"""
        if self.is_chrome_installed():
            logger.info("Chrome zaten kurulu")
            return True
        
        logger.info("Chrome kurulu değil, kurulum başlatılıyor...")
        
        try:
            # install_chrome.py scriptini çalıştır
            install_script = Path("install_chrome.py")
            if install_script.exists():
                result = subprocess.run(
                    [sys.executable, str(install_script)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logger.info("Chrome kurulumu başarılı")
                    self.find_chrome_executable()
                    return self.is_chrome_installed()
                else:
                    logger.error(f"Chrome kurulumu başarısız: {result.stderr}")
            else:
                logger.error("install_chrome.py dosyası bulunamadı")
                
        except Exception as e:
            logger.error(f"Chrome kurulumu sırasında hata: {e}")
        
        return False

# Global instance
chrome_manager = ChromeManager() 
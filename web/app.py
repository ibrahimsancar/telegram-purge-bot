from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from . import crud, models
from .database import SessionLocal, engine
from utils import bot_manager
from utils.bot_commands import set_bot_commands
from config import save_bot_token, get_bot_token, get_delete_service_messages, set_delete_service_messages
from telegram.ext import Application

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Web için log yapılandırması
def setup_web_logging():
    """Web uygulaması için logging yapılandırması"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    env_name = os.getenv("ENV", "development")
    web_log_file = log_dir / f"web_{env_name}.log"
    
    # Web logger
    web_logger = logging.getLogger("web")
    web_logger.setLevel(logging.INFO)
    
    # Web için file handler
    web_file_handler = RotatingFileHandler(
        web_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,  # 3 yedek dosya
        encoding='utf-8'
    )
    web_file_handler.setLevel(logging.INFO)
    web_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    web_file_handler.setFormatter(web_formatter)
    
    web_logger.addHandler(web_file_handler)
    
    return web_logger

# Web logging'i başlat
web_logger = setup_web_logging()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    web_logger.info("Ana sayfa ziyaret edildi")
    stats = crud.get_stats(db)
    history = crud.get_history(db, limit=10)
    return templates.TemplateResponse("index.html", {"request": request, "stats": stats, "history": history})

@app.get("/help", response_class=HTMLResponse)
async def read_help(request: Request):
    web_logger.info("Yardım sayfası ziyaret edildi")
    return templates.TemplateResponse("yardim.html", {"request": request})

@app.get("/api/stats")
async def api_get_stats(db: Session = Depends(get_db)):
    stats = crud.get_stats(db)
    history = crud.get_history(db, limit=10)
    return {"stats": stats, "history": history}

@app.post("/api/bot/start")
async def api_start_bot():
    return bot_manager.start_bot()

@app.post("/api/bot/stop")
async def api_stop_bot():
    return bot_manager.stop_bot()

@app.post("/api/bot/restart")
async def api_restart_bot():
    return bot_manager.restart_bot()

@app.get("/api/bot/status")
async def api_get_bot_status():
    status_info = bot_manager.get_bot_status()
    status_info["token"] = get_bot_token() # Token bilgisini ekle
    return status_info

@app.post("/api/bot/set_token")
async def api_set_bot_token(token_data: dict):
    token = token_data.get("token")
    if token:
        save_bot_token(token)
        return {"status": "success", "message": "Bot token başarıyla kaydedildi."}
    return {"status": "error", "message": "Geçersiz token."}

@app.get("/api/bot/get_token")
async def api_get_bot_token():
    token = get_bot_token()
    return {"token": token}

@app.post("/api/bot/set_commands")
async def api_set_bot_commands():
    token = get_bot_token()
    if not token:
        return {"status": "error", "message": "Bot token ayarlanmamış."}
    try:
        app_commands = Application.builder().token(token).build()
        await set_bot_commands(app_commands.bot)
        return {"status": "success", "message": "Bot komutları başarıyla ayarlandı."}
    except Exception as e:
        return {"status": "error", "message": f"Bot komutları ayarlanırken hata oluştu: {e}"}

@app.get("/api/settings/delete_service_messages")
async def api_get_delete_service_messages():
    value = get_delete_service_messages()
    return {"value": value}

@app.post("/api/settings/delete_service_messages")
async def api_set_delete_service_messages(setting_data: dict):
    value = setting_data.get("value")
    if isinstance(value, bool):
        set_delete_service_messages(value)
        return {"status": "success", "message": "Servis mesajı ayarı başarıyla kaydedildi."}
    return {"status": "error", "message": "Geçersiz değer."}

# HTML Panel için ek endpoint'ler
@app.get("/api/activities")
async def api_get_activities(db: Session = Depends(get_db)):
    """HTML panel için aktivite geçmişi"""
    history = crud.get_history(db, limit=20)
    activities = []
    for item in history:
        activities.append({
            "id": item.timestamp,
            "action": item.command,
            "description": f"{item.deleted_messages} mesaj silindi",
            "timestamp": item.timestamp,
            "status": "success"
        })
    return {"activities": activities}

@app.get("/api/bot/info")
async def api_get_bot_info():
    """Bot hakkında detaylı bilgi"""
    status_info = bot_manager.get_bot_status()
    token = get_bot_token()
    service_messages = get_delete_service_messages()
    
    return {
        "status": status_info,
        "token": token,
        "deleteServiceMessages": service_messages,
        "version": "1.0.0",
        "developer": "https://x.com/ibrahimsancar0"
    }

@app.get("/api/logs")
async def get_logs(limit: int = 20):
    """Son log kayıtlarını döndür"""
    try:
        log_dir = Path("logs")
        env_name = os.getenv("ENV", "development")
        bot_log_file = log_dir / f"purge_bot_{env_name}.log"
        
        if not bot_log_file.exists():
            return {"logs": [], "message": "Log dosyası bulunamadı"}
        
        # Son satırları oku
        with open(bot_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Son limit kadar satırı al ve parse et
        recent_logs = []
        for line in lines[-limit:]:
            line = line.strip()
            if line:
                # Log formatını parse et: 2025-06-27 02:32:10,823 - root - INFO - start_bot_polling:102 - Bot başlatılıyor...
                try:
                    parts = line.split(' - ', 4)
                    if len(parts) >= 5:
                        timestamp = parts[0]
                        module = parts[1]
                        level = parts[2]
                        function_line = parts[3]
                        message = parts[4]
                        
                        # Level'a göre icon belirle
                        icon_map = {
                            'DEBUG': '🔍',
                            'INFO': 'ℹ️',
                            'WARNING': '⚠️',
                            'ERROR': '❌',
                            'CRITICAL': '🚨'
                        }
                        icon = icon_map.get(level, '📝')
                        
                        recent_logs.append({
                            'timestamp': timestamp,
                            'module': module,
                            'level': level,
                            'message': message,
                            'icon': icon,
                            'function': function_line
                        })
                    elif len(parts) >= 4:
                        # Alternatif format: timestamp - module - LEVEL - message
                        timestamp = parts[0]
                        module = parts[1]
                        level = parts[2]
                        message = parts[3]
                        
                        icon_map = {
                            'DEBUG': '🔍',
                            'INFO': 'ℹ️',
                            'WARNING': '⚠️',
                            'ERROR': '❌',
                            'CRITICAL': '🚨'
                        }
                        icon = icon_map.get(level, '📝')
                        
                        recent_logs.append({
                            'timestamp': timestamp,
                            'module': module,
                            'level': level,
                            'message': message,
                            'icon': icon,
                            'function': ''
                        })
                except:
                    # Parse edilemeyen satırları basit format ile ekle
                    recent_logs.append({
                        'timestamp': '',
                        'module': '',
                        'level': 'INFO',
                        'message': line,
                        'icon': '📝',
                        'function': ''
                    })
        
        return {"logs": recent_logs[::-1]}  # En yeni en üstte
        
    except Exception as e:
        web_logger.error(f"Log okuma hatası: {e}")
        return {"logs": [], "error": str(e)}

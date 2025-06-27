from sqlalchemy.orm import Session
from web import crud
from web.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def increment_total_deleted(count: int = 1):
    db = next(get_db())
    crud.increment_stat(db, 'total_deleted_messages', count)

def increment_total_purges(count: int = 1):
    db = next(get_db())
    crud.increment_stat(db, 'total_purge_commands', count)

def add_history_entry(chat_id: str, command: str, deleted_messages: int):
    db = next(get_db())
    crud.add_history(db, chat_id, command, deleted_messages)

def update_active_groups(count: int):
    db = next(get_db())
    crud.update_stat(db, 'active_groups', count) 
from sqlalchemy.orm import Session
from . import models

def get_stats(db: Session):
    stats = db.query(models.Stats).all()
    return {s.key: s.value for s in stats}

def update_stat(db: Session, key: str, value: int):
    stat = db.query(models.Stats).filter(models.Stats.key == key).first()
    if stat:
        stat.value = value
    else:
        stat = models.Stats(key=key, value=value)
        db.add(stat)
    db.commit()
    db.refresh(stat)
    return stat

def increment_stat(db: Session, key: str, amount: int = 1):
    stat = db.query(models.Stats).filter(models.Stats.key == key).first()
    if stat:
        stat.value += amount
    else:
        stat = models.Stats(key=key, value=amount)
        db.add(stat)
    db.commit()
    db.refresh(stat)
    return stat

def add_history(db: Session, chat_id: str, command: str, deleted_messages: int):
    history_entry = models.History(
        chat_id=chat_id,
        command=command,
        deleted_messages=deleted_messages
    )
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)
    return history_entry

def get_history(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.History).order_by(models.History.timestamp.desc()).offset(skip).limit(limit).all()

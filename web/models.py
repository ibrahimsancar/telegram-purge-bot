from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
import datetime

class Stats(Base):
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Integer, default=0)

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String)
    command = Column(String)
    deleted_messages = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

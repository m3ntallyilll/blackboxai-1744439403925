from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Create database engine
engine = create_engine('sqlite:///instance/email_manager.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Import models after Base is defined
from .subscription import User, Subscription

class EmailHistory(Base):
    __tablename__ = 'email_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    sender = Column(String(255))
    subject = Column(String(255))
    processed_at = Column(DateTime, default=datetime.utcnow)
    category = Column(String(50))
    importance = Column(String(20))
    sentiment = Column(String(20))
    ai_analysis = Column(String(1000))
    suggested_actions = Column(String(500))
    
    user = relationship("User")

def init_db():
    Base.metadata.create_all(engine)

__all__ = ['User', 'Subscription', 'EmailHistory', 'Session', 'init_db', 'Base']

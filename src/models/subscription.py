from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..models import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    
    @property
    def has_active_subscription(self):
        return self.subscription and self.subscription.is_active

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    plan_type = Column(String(50))  # 'monthly' or 'lifetime'
    status = Column(String(20))  # 'active', 'cancelled', 'expired'
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    amount_paid = Column(Float)
    api_key = Column(String(255), nullable=True)  # For lifetime subscribers
    
    user = relationship("User", back_populates="subscription")

    @property
    def is_active(self):
        if self.status != 'active':
            return False
        if self.plan_type == 'lifetime':
            return True
        return self.end_date is None or self.end_date > datetime.utcnow()

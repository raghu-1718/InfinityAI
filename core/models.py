
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

# --- AI/ML Trading System Models ---
class Model(Base):
    __tablename__ = 'models'
    model_id = Column(Integer, primary_key=True)
    version = Column(String, nullable=False)
    type = Column(String, nullable=False)
    parameters = Column(JSON, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='active')

class Prediction(Base):
    __tablename__ = 'predictions'
    prediction_id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('models.model_id'))
    symbol = Column(String, nullable=False)
    prediction_value = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Signal(Base):
    __tablename__ = 'signals'
    signal_id = Column(Integer, primary_key=True)
    strategy_type = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    signal_strength = Column(Float, nullable=True)
    entry_price = Column(Float, nullable=True)
    status = Column(String, default='pending')
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Backtest(Base):
    __tablename__ = 'backtests'
    backtest_id = Column(Integer, primary_key=True)
    strategy_config = Column(JSON, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default='user')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # Dhan API credentials
    dhan_client_id = Column(String, nullable=True)
    dhan_access_token = Column(String, nullable=True)
    trades = relationship('TradeLog', back_populates='user')

class TradeLog(Base):
    __tablename__ = 'trade_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    symbol = Column(String, nullable=False)
    action = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship('User', back_populates='trades')

class AuditTrail(Base):
    __tablename__ = 'audit_trails'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String, nullable=False)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Analytics(Base):
    __tablename__ = 'analytics'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    metric = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

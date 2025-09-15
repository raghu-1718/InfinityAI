
<<<<<<< HEAD
import csv
import os
import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_trade(user_id, trade_data):
	filename = os.path.join(LOG_DIR, f"{user_id}_trades.csv")
	file_exists = os.path.isfile(filename)

	trade_data.setdefault("timestamp", datetime.datetime.now().isoformat())
	trade_data["user_id"] = user_id

	with open(filename, "a", newline="") as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=trade_data.keys())
		if not file_exists:
			writer.writeheader()
		writer.writerow(trade_data)

def get_trade_logs(user_id, limit=100):
	filename = os.path.join(LOG_DIR, f"{user_id}_trades.csv")
	if not os.path.exists(filename):
		return []
	with open(filename, "r") as csvfile:
		reader = list(csv.DictReader(csvfile))
		return list(reversed(reader[-limit:]))
=======
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import TradeLog, Base
import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///infinityai.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def log_trade(user_id, trade_data):
	session = SessionLocal()
	trade = TradeLog(
		user_id=user_id,
		symbol=trade_data.get("symbol"),
		action=trade_data.get("action"),
		quantity=trade_data.get("quantity"),
		price=trade_data.get("price"),
		timestamp=trade_data.get("timestamp", datetime.datetime.now())
	)
	session.add(trade)
	session.commit()
	session.close()

def get_trade_logs(user_id, limit=100):
	session = SessionLocal()
	trades = session.query(TradeLog).filter_by(user_id=user_id).order_by(TradeLog.timestamp.desc()).limit(limit).all()
	session.close()
	return [trade.__dict__ for trade in trades]
>>>>>>> 7ee6d5f999d9bc01dbdc4b984f791a0af547bcda

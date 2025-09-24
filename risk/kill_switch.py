from datetime import date
from threading import Lock

class KillSwitch:
    def __init__(self, daily_loss_limit: float = 0):
        self._active = False
        self._lock = Lock()
        self.daily_loss_limit = daily_loss_limit
        self._loss_today = 0.0
        self._loss_date = date.today()

    def activate(self, reason: str = ""):
        with self._lock:
            self._active = True

    def deactivate(self):
        with self._lock:
            self._active = False

    def reset_if_new_day(self):
        with self._lock:
            if self._loss_date != date.today():
                self._loss_date = date.today()
                self._loss_today = 0.0

    def record_pnl(self, realized_delta: float):
        self.reset_if_new_day()
        if realized_delta < 0:
            with self._lock:
                self._loss_today += -realized_delta
                if self.daily_loss_limit > 0 and self._loss_today >= self.daily_loss_limit:
                    self._active = True

    def is_active(self):
        self.reset_if_new_day()
        return self._active

    def status(self):
        return {
            "active": self._active,
            "loss_today": self._loss_today,
            "daily_loss_limit": self.daily_loss_limit,
            "date": str(self._loss_date),
        }

_kill = None

def init_kill_switch(limit: float):
    global _kill
    if _kill is None:
        _kill = KillSwitch(limit)
    return _kill

def get_kill_switch():
    return _kill

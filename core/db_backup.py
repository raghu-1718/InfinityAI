import os
import shutil
from datetime import datetime

def backup_database(db_path, backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path

def restore_database(backup_path, db_path):
    shutil.copy2(backup_path, db_path)
    return db_path

"""
Notification service (simulé) : écrit un résumé dans notifications.log
"""
import os
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "notifications.log")

def notify(request_id: str, to_email: str, message: str):
    """Enregistre une notification simulée dans notifications.log"""
    now = datetime.utcnow().isoformat()
    entry = f"{now} | {request_id} | to={to_email} | {message}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)

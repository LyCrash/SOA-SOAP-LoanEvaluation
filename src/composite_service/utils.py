"""
Utilitaires du composite :
- génération d'IDs simples,
- lecture/écriture de la "DB" JSON.
"""
import json
import os
import uuid
from typing import Dict, Any
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "notifications.log")

def ensure_db():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump({"requests": {}}, f, indent=2, ensure_ascii=False)

def read_db() -> Dict[str, Any]:
    ensure_db()
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def write_db(db: Dict[str, Any]):
    ensure_db()
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def new_request_id() -> str:
    """Retourne un identifiant unique simple pour une demande."""
    return "REQ-" + uuid.uuid4().hex[:8].upper()

def notify(request_id: str, to_email: str, message: str):
    """Enregistre une notification simulée dans notifications.log"""
    now = datetime.utcnow().isoformat()
    entry = f"{now} | {request_id} | to={to_email} | {message}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


"""
Utilitaires du service composite :
- Gestion de la base de données JSON,
- Génération d'identifiants simples,
- Notifications simulées.
"""
import json
import os
from typing import Dict, Any
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "database.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "notifications.log")


# --- Base de données JSON --- #
def ensure_db():
    """Crée la base JSON si elle n'existe pas."""
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump({"requests": {}}, f, indent=2, ensure_ascii=False)


def read_db() -> Dict[str, Any]:
    """Lit la base JSON et corrige si structure manquante."""
    ensure_db()
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
            if not isinstance(db, dict):
                db = {"requests": {}}
            if "requests" not in db:
                db["requests"] = {}
            return db
    except (json.JSONDecodeError, FileNotFoundError):
        # Réinitialise en cas de fichier vide ou corrompu
        write_db({"requests": {}})
        return {"requests": {}}


def write_db(db: Dict[str, Any]):
    """Écrit la base JSON complète."""
    ensure_db()
    if "requests" not in db:
        db["requests"] = {}
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def save_request(request_id: str, decision: Dict[str, Any]):
    """Sauvegarde une décision dans la base JSON."""
    db = read_db()
    if "requests" not in db:
        db["requests"] = {}
    db["requests"][request_id] = {
        "result": decision,
        "timestamp": datetime.utcnow().isoformat()
    }
    write_db(db)


def get_request(request_id: str) -> Dict[str, Any]:
    """Récupère une demande par son ID."""
    db = read_db()
    return db.get("requests", {}).get(request_id)


# --- Identifiant --- #
def new_request_id(request_text: str) -> str:
    """Génère un identifiant basé sur le hash du texte."""
    return "REQ_" + str(abs(hash(request_text)) % 10000)


# --- Notifications --- #
def notify(request_id: str, to_email: str, message: str):
    """Enregistre une notification simulée dans un fichier log."""
    now = datetime.utcnow().isoformat()
    entry = f"{now} | {request_id} | to={to_email} | {message}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)

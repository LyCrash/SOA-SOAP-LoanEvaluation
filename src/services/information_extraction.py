"""
Service d'extraction d'information (IE) : très basique,
utilise la recherche de lignes clefs dans le texte pour produire un dictionnaire.
"""
import re
from typing import Dict

def extract_information(text: str) -> Dict:
    """
    Extrait de façon simple des champs depuis le texte de la demande.
    Retourne un dict contenant : name, address, email, phone, loan_amount, loan_duration_years,
    property_description, monthly_income, monthly_expenses
    """
    # Patterns simples (robustes pour l'exemple, pas production)
    def find(pattern):
        m = re.search(pattern, text, flags=re.IGNORECASE)
        return m.group(1).strip() if m else None

    info = {
        "name": find(r"Nom du Client:\s*(.+)"),
        "address": find(r"Adresse:\s*(.+)"),
        "email": find(r"Email:\s*(\S+)"),
        "phone": find(r"Numéro de Téléphone:\s*(.+)"),
        "loan_amount": find(r"Montant du Prêt Demandé:\s*([0-9\.,\sA-Za-z€]+)"),
        "loan_duration": find(r"Durée du Prêt:\s*([0-9]+)\s*ans"),
        "property_description": find(r"Description de la Propriété:\s*(.+)"),
        "monthly_income": find(r"Revenu Mensuel:\s*([0-9\.,\sA-Za-z€]+)"),
        "monthly_expenses": find(r"Dépenses Mensuelles:\s*([0-9\.,\sA-Za-z€]+)"),
    }

    # Nettoyage numérique
    def parse_money(s):
        if not s: return None
        s = s.replace("€","").replace("EUR","").replace(",","").strip()
        digits = re.findall(r"[\d]+", s)
        return int("".join(digits)) if digits else None

    info["loan_amount_eur"] = parse_money(info["loan_amount"])
    info["monthly_income_eur"] = parse_money(info["monthly_income"])
    info["monthly_expenses_eur"] = parse_money(info["monthly_expenses"])
    info["loan_duration_years"] = int(info["loan_duration"]) if info["loan_duration"] else None

    return info

"""
Service de vérification de solvabilité (stub).
Calcule un "score" simple et retourne des éléments d'explication.
"""
from typing import Dict

def check_credit(extracted: Dict) -> Dict:
    """
    Calcule un score fictif et retourne un dict :
    {score: int, debt_ratio: float, details: str}
    Règles simples :
    - score de base 650
    - si income-expenses élevé -> + points
    - si ratio dépenses/revenu > 0.5 -> pénalité
    """
    income = extracted.get("monthly_income_eur") or 0
    expenses = extracted.get("monthly_expenses_eur") or 0
    debt_ratio = round(expenses / income, 2) if income > 0 else 1.0

    score = 650
    # bonus based on surplus
    surplus = max(0, income - expenses)
    score += min(100, int(surplus / 50))  # 1 point per 50€ of surplus, up to 100
    # penalty for high debt ratio
    if debt_ratio > 0.6:
        score -= 80
    elif debt_ratio > 0.5:
        score -= 40
    elif debt_ratio > 0.4:
        score -= 10

    details = f"Income={income}€, Expenses={expenses}€, DebtRatio={debt_ratio}"
    return {"score": max(300, score), "debt_ratio": debt_ratio, "details": details}

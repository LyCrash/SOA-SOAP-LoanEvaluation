"""
Service de décision : agrège score credit + evaluation propriété + règles de l'institution.
Retourne 'APPROVED' ou 'REJECTED' avec explications.
"""
from typing import Dict

def decide(extracted: Dict, credit: Dict, property_eval: Dict) -> Dict:
    """
    Règles simplifiées :
    - threshold_score = 700
    - loan must be <= estimated_value * 0.8
    - debt_ratio must be < 0.5
    """
    score = credit.get("score")
    debt_ratio = credit.get("debt_ratio")
    est_value = property_eval.get("estimated_value") or 0
    loan = extracted.get("loan_amount_eur") or 0

    reasons = []
    approved = True

    if score < 700:
        approved = False
        reasons.append(f"Credit score too low ({score} < 700).")
    if debt_ratio is not None and debt_ratio >= 0.5:
        approved = False
        reasons.append(f"High debt-to-income ratio ({debt_ratio} >= 0.5).")
    if loan > est_value * 0.8:
        approved = False
        reasons.append(f"Loan amount {loan}€ exceeds 80% of property value ({est_value}€).")

    if approved:
        decision = "APPROVED"
        details = "All checks passed."
    else:
        decision = "REJECTED"
        details = " ; ".join(reasons) if reasons else "Rejected by policy."

    return {"decision": decision, "details": details, "score": score, "estimated_value": est_value}

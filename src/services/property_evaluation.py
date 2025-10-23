"""
Service d'évaluation de la propriété (stub).
Retourne une estimation fictive de la valeur de marché et une conformité.
"""
from typing import Dict

def evaluate_property(extracted: Dict) -> Dict:
    """
    Estime la valeur marchande en fonction du texte.
    Méthode simple : si description contient "quartier résidentiel" -> + bonus.
    """
    desc = (extracted.get("property_description") or "").lower()
    base_value = 200000  # valeur par défaut
    if "deux étages" in desc or "maison à deux étages" in desc:
        base_value += 20000
    if "quartier résidentiel" in desc:
        base_value += 15000
    # conformité simple
    compliant = True  # stub : on suppose conforme
    return {"estimated_value": base_value, "compliant": compliant, "details": f"description_length={len(desc)}"}

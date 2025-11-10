import json
from suds.client import Client

COMPOSITE = "http://127.0.0.1:8000/LoanEvaluationService?wsdl"
client = Client(COMPOSITE)

# # Approved
# loan_text = """
# Nom du Client: Sophie Durand
# Adresse: 10 Boulevard Victor Hugo, Montpellier
# Email: sophie.durand@email.com
# Numéro de Téléphone: +33699112233
# Montant du Prêt Demandé: 150000
# Revenu Mensuel: 7200
# Dépenses Mensuelles: 1800
# Description de la Propriété: Appartement moderne de 90m² avec balcon et parking, situé en centre-ville, récemment rénové.
# """

# # Rejected
# loan_text = """
# Nom du Client: Julien Martin
# Adresse: 58 Rue du Lac, Bordeaux
# Email: julien.martin@email.com
# Numéro de Téléphone: +33666778899
# Montant du Prêt Demandé: 400000
# Revenu Mensuel: 5000
# Dépenses Mensuelles: 2500
# Description de la Propriété: Maison ancienne à rénover de 150m² située en périphérie de la ville.
# """

# Medium
loan_text = """
Nom du Client: Alice Dupont
Adresse: 12 rue des Lilas, Paris
Email: alice.dupont@email.com
Numéro de Téléphone: +33678912345
Montant du Prêt Demandé: 180000
Revenu Mensuel: 4200
Dépenses Mensuelles: 1200
Description de la Propriété: Appartement de 75m² situé dans un quartier calme, proche du centre-ville, bien entretenu.
"""


print("Submitting...")
resp_json = client.service.submitRequest(loan_text)
resp = json.loads(resp_json)
print(f"Request {json.dumps(resp['request_id'], indent=2, ensure_ascii=False)} submitted successfully")

if resp.get("status") == "done":
    print("\nFinal decision:")
    print(json.dumps(resp["decision"], indent=2, ensure_ascii=False))
    print(f"\nRequest ID: {resp['request_id']}")
else:
    print("\nError or unexpected response.")

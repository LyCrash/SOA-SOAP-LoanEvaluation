import json
from suds.client import Client

COMPOSITE = "http://127.0.0.1:8000/LoanEvaluationService?wsdl"
client = Client(COMPOSITE)

loan_text = """
Nom du Client: Marc Lefevre
Adresse: 25 Avenue des Sciences, Lyon
Email: marc.lefevre@email.com
Numéro de Téléphone: +33677889900
Montant du Prêt Demandé: 200000
Revenu Mensuel: 6500
Dépenses Mensuelles: 1500
Description de la Propriété: Maison individuelle récente de 120m² avec jardin, située dans un quartier résidentiel calme. État du bien excellent.
"""

print("Submitting (likely APPROVE) ...")
resp_json = client.service.submitRequest(loan_text)
resp = json.loads(resp_json)
print(f"Request {json.dumps(resp['request_id'], indent=2, ensure_ascii=False)} submitted successfully")

if resp.get("status") == "done":
    print("\nFinal decision:")
    print(json.dumps(resp["decision"], indent=2, ensure_ascii=False))
    print(f"\nRequest ID: {resp['request_id']}")
else:
    print("\nError or unexpected response.")

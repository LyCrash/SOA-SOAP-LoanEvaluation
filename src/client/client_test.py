import json
from suds.client import Client

COMPOSITE = "http://127.0.0.1:8000/LoanEvaluationService?wsdl"
client = Client(COMPOSITE)

loan_text = """
Nom du Client: Jeanne Petit
Adresse: 5 Rue des Fleurs, Paris
Email: jeanne.petit@email.com
Numéro de Téléphone: +33600111222
Montant du Prêt Demandé: 300000
Revenu Mensuel: 2000
Dépenses Mensuelles: 1500
Description de la Propriété: Petit appartement ancien, nécessite quelques travaux, proche d'une route passante.
"""

print("Submitting (likely REJECT) ...")
resp_json = client.service.submitRequest(loan_text)
resp = json.loads(resp_json)
print(f"Request {json.dumps(resp['request_id'], indent=2, ensure_ascii=False)} submitted successfully")

# The service is synchronous: decision is included in response.
if resp.get("status") == "done":
    print("\nFinal decision:")
    print(json.dumps(resp["decision"], indent=2, ensure_ascii=False))
    print(f"\nRequest ID: {resp['request_id']}")
else:
    print("\nError or unexpected response.")

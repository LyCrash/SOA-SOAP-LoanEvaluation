from suds.client import Client
import json

COMPOSITE_URL = "http://127.0.0.1:8000/LoanEvaluationService?wsdl"

client = Client(COMPOSITE_URL)

text = """
Nom du Client: John Doe
Adresse: 123 Rue de la Liberté, 75001 Paris, France
Email: john.doe@email.com
Numéro de Téléphone: +33 123 456 789
Montant du Prêt Demandé: 200000
Durée du Prêt: 20 ans
Description de la Propriété: Maison à deux étages avec jardin, située dans un quartier résidentiel calme.
Revenu Mensuel: 5000
Dépenses Mensuelles: 1000
"""

result_json = client.service.submitRequest(text)
print("\n=== Response ===")
print(result_json)
print("\nParsed:", json.loads(result_json))

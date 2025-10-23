"""
Client de test (SUDS) :
- appelle SubmitLoanRequest(text) avec l'exemple fourni
- récupère immediately le request_id et appelle GetEvaluation(request_id)
"""
from suds.client import Client
import time

url = "http://127.0.0.1:8000/ServiceWebComposite"
client = Client(f"{url}?wsdl")

# Exemple de texte
sample_text = """Nom du Client: John Doe
Adresse: 123 Rue de la Liberté, 75001 Paris, France
Email: john.doe@email.com
Numéro de Téléphone: +33 123 456 789
Montant du Prêt Demandé: 200000 EUR
Durée du Prêt: 20 ans
Description de la Propriété: Maison à deux étages avec jardin, située dans un quartier résidentiel calme.
Revenu Mensuel: 5000 EUR
Dépenses Mensuelles: 3000 EUR
"""

print("🟢 Submitting the loan request for evaluation...")
request_id = client.service.SubmitLoanRequest(sample_text)
print(f"✅ Request submitted successfully with ID: {request_id}")

# On attend un peu (ici c'est synchrone donc pas nécessaire) puis récupère l'évaluation
time.sleep(0.5)
print("\nGetting evaluation result...")
result_text = client.service.GetEvaluation(request_id)
print("\n📊 --- Loan Evaluation Result ---")
print(result_text)
print("--------------------------------------")

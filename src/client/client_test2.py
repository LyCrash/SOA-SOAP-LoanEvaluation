"""
Client test script for a positive (approved) loan request scenario.
This connects to the SOAP composite service running on localhost:8000.
"""

from suds.client import Client
import time

# --- URL of the running SOAP composite service ---
url = "http://127.0.0.1:8000/ServiceWebComposite"

# Initialize the SOAP client
client = Client(f"{url}?wsdl")

# --- Example of a loan request with good financial health ---
loan_request_text = """
Nom du Client: Alice Martin
Adresse: 12 Avenue des Champs-Élysées, 75008 Paris, France
Email: alice.martin@email.com
Numéro de Téléphone: +33 612 345 678
Montant du Prêt Demandé: 180000 EUR
Durée du Prêt: 15 ans
Description de la Propriété: Appartement moderne de 3 pièces situé dans le 8e arrondissement de Paris.
Revenu Mensuel: 7200 EUR
Dépenses Mensuelles: 2500 EUR
"""

print("🟢 Submitting the loan request for evaluation...")

# --- Step 1: Submit the loan request ---
request_id = client.service.SubmitLoanRequest(loan_request_text)
print(f"✅ Request submitted successfully with ID: {request_id}")

# --- Step 2: Retrieve the evaluation result ---
response_result = client.service.GetEvaluation(request_id)
time.sleep(0.5)

print("\nGetting evaluation result...")
result_text = client.service.GetEvaluation(request_id)
print("\n📊 --- Loan Evaluation Result ---")
print(result_text)
print("--------------------------------------")

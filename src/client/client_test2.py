import json
from suds.client import Client
import time

COMPOSITE_URL = "http://127.0.0.1:8000/LoanEvaluationService?wsdl"

if __name__ == "__main__":
    # Example natural-language loan request
    request_text = """
    Nom du Client: Alice Dupont
    Adresse: 12 rue des Lilas, Lyon
    Email: alice.dupont@example.com
    Numéro de Téléphone: 0601020304
    Montant du Prêt Demandé: 200000
    Revenu Mensuel: 4500
    Dépenses Mensuelles: 1800
    Description de la Propriété: Appartement de 4 pièces situé dans un quartier calme, proche des transports.
    """

    print("[Client] Connecting to composite service...")
    client = Client(COMPOSITE_URL)

    print("[Client] Submitting request...")
    response = client.service.submitRequest(request_text)
    

    try:
        parsed = json.loads(response)
        print("=== Parsed Response ===")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print(f"\n=== Raw Response ===\n{response}\n")
        parsed = {}

    # Optionally, fetch results later using getResult
    if "request_id" in parsed:
        request_id = parsed["request_id"]
        print(f"\n[Client] Fetching result for request_id={request_id}...")
        time.sleep(1.5)
        result = client.service.getResult(request_id)
        try:
            result_json = json.loads(result)
            print(json.dumps(result_json, indent=2, ensure_ascii=False))
        except Exception:
            print(f"\n=== getResult() ===\n{result}\n")
            pass

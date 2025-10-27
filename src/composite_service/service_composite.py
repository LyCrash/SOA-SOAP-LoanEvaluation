import sys
import os
import logging
import json
from datetime import datetime
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
from suds.client import Client

# Import utils robustement (fonctionne en mode package ou exécution directe)
try:
    from composite_service.utils import (
        new_request_id, notify, save_request, get_request, read_db, write_db
    )
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(__file__))
    from utils import new_request_id, notify, save_request, get_request, read_db, write_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("composite")

# --- Endpoints des services enfants ---
IE_URL = "http://127.0.0.1:8001/InformationExtractionService?wsdl"
CC_URL = "http://127.0.0.1:8002/CreditCheckService?wsdl"
PE_URL = "http://127.0.0.1:8003/PropertyEvaluationService?wsdl"
DS_URL = "http://127.0.0.1:8004/DecisionService?wsdl"

# --- DB file is managed by utils (read_db/write_db) ---

class LoanEvaluationComposite(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def submitRequest(ctx, request_text):
        """
        Accepts a natural-language loan request (text), orchestrates the IE->CC->PE->DS pipeline,
        stores a comprehensive record in the JSON DB and triggers a notification.
        Returns a JSON string with request_id and decision summary.
        """
        try:
            logger.info("[Composite] New submission received.")
            # create suds clients (lightweight)
            ie_client = Client(IE_URL)
            cc_client = Client(CC_URL)
            pe_client = Client(PE_URL)
            ds_client = Client(DS_URL)

            # 1) Information Extraction
            ie_response = ie_client.service.extract_information(request_text)
            # ie_response is expected to be a JSON string
            try:
                applicant = json.loads(ie_response)
            except Exception:
                # defensive fallback
                applicant = {"nom": "Inconnu", "adresse": "Non spécifiée", "email": "unknown@email.com",
                             "montant_pret": 0.0, "revenu_mensuel": 0.0, "depenses_mensuelles": 0.0,
                             "description": request_text[:500]}

            logger.info(f"[Composite] IE -> applicant keys: {list(applicant.keys())}")

            # 2) Credit Check (send applicant JSON string)
            cc_response = cc_client.service.check_credit(json.dumps(applicant))
            try:
                cc_parsed = json.loads(cc_response)
            except Exception:
                cc_parsed = {"error": "invalid_response_from_cc"}
            logger.info(f"[Composite] CC -> {cc_parsed.get('credit_score', 'N/A')}")

            # 3) Property Evaluation (send applicant JSON string; service uses adresse+description)
            pe_response = pe_client.service.evaluate_property(json.dumps(applicant))
            try:
                pe_parsed = json.loads(pe_response)
            except Exception:
                pe_parsed = {"error": "invalid_response_from_pe"}
            logger.info(f"[Composite] PE -> property_value: {pe_parsed.get('property_value', 'N/A')}")

            # 4) Prepare data for Decision Service.
            # Decision service expects credit_score, property_value, loan_amount, revenu_mensuel, depenses_mensuelles, emploi_stable, description, adresse
            decision_input = {
                "credit_score": float(cc_parsed.get("credit_score", 0)) if isinstance(cc_parsed.get("credit_score", None), (int, float, str)) else 0,
                "property_value": float(pe_parsed.get("property_value", 0)) if isinstance(pe_parsed.get("property_value", None), (int, float, str)) else 0,
                "loan_amount": float(applicant.get("montant_pret", 0)) if applicant.get("montant_pret", None) not in (None, "") else 0,
                "revenu_mensuel": float(applicant.get("revenu_mensuel", 0)) if applicant.get("revenu_mensuel", None) not in (None, "") else 0,
                "depenses_mensuelles": float(applicant.get("depenses_mensuelles", 0)) if applicant.get("depenses_mensuelles", None) not in (None, "") else 0,
                "emploi_stable": applicant.get("emploi_stable", "oui") in ("oui", "true", True, "True"),
                "description": applicant.get("description", ""),
                "adresse": applicant.get("adresse", "")
            }

            # Add some optional fields if available
            for optional in ("nom", "prenom", "email", "telephone", "age"):
                if optional in applicant:
                    decision_input[optional] = applicant[optional]

            logger.info(f"[Composite] Decision input prepared: keys={list(decision_input.keys())}")

            # 5) Decision call
            ds_response = ds_client.service.make_decision(json.dumps(decision_input))
            try:
                decision_parsed = json.loads(ds_response)
            except Exception:
                decision_parsed = {"error": "invalid_response_from_ds"}

            logger.info(f"[Composite] Decision -> approved: {decision_parsed.get('approved', 'N/A')}")

            # 6) Persist full enriched record into DB (read-modify-write)
            request_id = new_request_id(request_text)
            timestamp = datetime.utcnow().isoformat()

            db = read_db()
            # Ensure structure
            if "requests" not in db:
                db["requests"] = {}

            full_record = {
                "request_id": request_id,
                "timestamp": timestamp,
                "raw_text": request_text,
                "applicant": applicant,
                "credit_check": cc_parsed,
                "property_evaluation": pe_parsed,
                "decision": decision_parsed
            }

            db["requests"][request_id] = full_record
            write_db(db)

            # 7) Save a compact decision for quick access (backwards-compatible)
            try:
                save_request(request_id, decision_parsed)
            except Exception:
                logger.warning("[Composite] save_request failed; continuing.")

            # 8) Notification (simulated)
            email = applicant.get("email", "unknown@email.com")
            # build a short notification message (human readable)
            msg = f"Votre demande {request_id} a été traitée. Résultat: {decision_parsed.get('message', 'N/A')}."
            try:
                notify(request_id, email, msg)
            except Exception:
                logger.warning("[Composite] notify() raised an exception, continuing.")

            # 9) Return summary JSON to client
            response = {
                "request_id": request_id,
                "timestamp": timestamp,
                "applicant_name": applicant.get("nom", "Inconnu"),
                "decision_summary": {
                    "approved": decision_parsed.get("approved", False),
                    "message": decision_parsed.get("message", ""),
                    "interest_rate": decision_parsed.get("interest_rate", None)
                }
            }

            return json.dumps(response, ensure_ascii=False)

        except Exception as e:
            logger.error(f"[Composite] Fatal error: {e}", exc_info=True)
            return json.dumps({"status": "error", "message": str(e)})

    @rpc(Unicode, _returns=Unicode)
    def getResult(ctx, request_id):
        """
        Return the full stored evaluation record for the given request_id.
        If not found, return a structured error.
        """
        try:
            record = get_request(request_id)
            if record:
                # get_request returns the stored object (previously saved by save_request)
                # but our DB stores full record under read_db; try to read full version
                db = read_db()
                full = db.get("requests", {}).get(request_id)
                if full:
                    return json.dumps(full, indent=2, ensure_ascii=False)
                # fallback to what get_request returned
                return json.dumps({"request_id": request_id, "result": record}, ensure_ascii=False)
            else:
                return json.dumps({"status": "error", "raison": "Aucune demande trouvée."})
        except Exception as e:
            logger.error(f"[Composite] getResult error: {e}", exc_info=True)
            return json.dumps({"status": "error", "message": str(e)})

# --- Spyne Application ---
app = Application(
    [LoanEvaluationComposite],
    tns='loan.composite',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    sys.exit(run_twisted([(WsgiApplication(app), b'LoanEvaluationService')], 8000))

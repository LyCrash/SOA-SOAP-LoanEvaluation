import sys, logging, json, os
from spyne import Application, rpc, ServiceBase, Unicode, AnyDict
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
from suds.client import Client

# Import robuste (compatible exécution directe et en package)
try:
    from composite_service.utils import (
        new_request_id, notify, save_request, get_request
    )
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(__file__))
    from utils import new_request_id, notify, save_request, get_request

logging.basicConfig(level=logging.INFO)

# --- URLs des services --- #
IE_URL = "http://127.0.0.1:8001/InformationExtractionService?wsdl"
CC_URL = "http://127.0.0.1:8002/CreditCheckService?wsdl"
PE_URL = "http://127.0.0.1:8003/PropertyEvaluationService?wsdl"
DS_URL = "http://127.0.0.1:8004/DecisionService?wsdl"


class LoanEvaluationComposite(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def submitRequest(ctx, request_text):
        """Soumet la demande et orchestre tous les sous-services."""
        try:
            ie = Client(IE_URL)
            cc = Client(CC_URL)
            pe = Client(PE_URL)
            ds = Client(DS_URL)

            # --- Extraction d'information --- #
            extracted = ie.service.extract_information(request_text)
            parsed = json.loads(extracted)

            # --- Vérification du crédit --- #
            score_json = cc.service.check_credit(extracted)
            score = json.loads(score_json)["credit_score"]

            # --- Évaluation du bien --- #
            property_json = pe.service.evaluate_property(extracted)
            property_value = json.loads(property_json)["property_value"]

            # --- Décision --- #
            data = {
                "credit_score": score,
                "property_value": property_value,
                "loan_amount": float(parsed.get("montant_pret", 0))
            }
            decision_json = ds.service.make_decision(json.dumps(data))
            decision = json.loads(decision_json)

            # --- Sauvegarde et notification --- #
            request_id = new_request_id(request_text)
            save_request(request_id, decision)

            notify(request_id, parsed.get("email", "unknown@email.com"), decision["message"])

            logging.info(f"[Composite] Décision enregistrée pour {request_id}")
            return json.dumps({"request_id": request_id, "decision": decision})

        except Exception as e:
            logging.error(f"Erreur composite: {e}", exc_info=True)
            return json.dumps({"status": "error", "message": str(e)})

    @rpc(Unicode, _returns=Unicode)
    def getResult(ctx, request_id):
        """Retourne le résultat d'une demande sauvegardée."""
        record = get_request(request_id)
        if record:
            return json.dumps(record["result"])
        return json.dumps({"status": "error", "raison": "Aucune demande trouvée."})


app = Application(
    [LoanEvaluationComposite],
    tns='loan.composite',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    sys.exit(run_twisted([(WsgiApplication(app), b'LoanEvaluationService')], 8000))

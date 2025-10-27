import sys, logging, json, os
from spyne import Application, rpc, ServiceBase, Unicode, AnyDict
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
from suds.client import Client

from datetime import datetime
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "notifications.log")
def notify(request_id: str, to_email: str, message: str):
    """Enregistre une notification simulée dans notifications.log"""
    now = datetime.utcnow().isoformat()
    entry = f"{now} | {request_id} | to={to_email} | {message}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)

logging.basicConfig(level=logging.INFO)

IE_URL = "http://127.0.0.1:8001/InformationExtractionService?wsdl"
CC_URL = "http://127.0.0.1:8002/CreditCheckService?wsdl"
PE_URL = "http://127.0.0.1:8003/PropertyEvaluationService?wsdl"
DS_URL = "http://127.0.0.1:8004/DecisionService?wsdl"
DB_FILE = "composite_service/database.json"

class LoanEvaluationComposite(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def submitRequest(ctx, request_text):
        ie = Client(IE_URL)
        cc = Client(CC_URL)
        pe = Client(PE_URL)
        ds = Client(DS_URL)

        extracted = ie.service.extract_information(request_text)
        parsed = json.loads(extracted)

        score_json = cc.service.check_credit(extracted)
        score = json.loads(score_json)["credit_score"]

        property_json = pe.service.evaluate_property(extracted)
        property_value = json.loads(property_json)["property_value"]

        data = {
            "credit_score": score,
            "property_value": property_value,
            "loan_amount": float(parsed.get("montant_pret", 0))
        }
        decision_json = ds.service.make_decision(json.dumps(data))
        decision = json.loads(decision_json)

        request_id = "REQ_" + str(abs(hash(request_text)) % 10000)
        record = {"request_id": request_id, "result": decision}
        with open(DB_FILE, "w") as f:
            json.dump(record, f, indent=4)

        notify(request_id, parsed.get("email", "unknown@email.com"), decision["message"])
        return json.dumps({"request_id": request_id, "decision": decision})

    @rpc(Unicode, _returns=Unicode)
    def getResult(ctx, request_id):
        with open(DB_FILE, "r") as f:
            data = json.load(f)
        if data["request_id"] == request_id:
            return json.dumps(data["result"])
        return json.dumps({"status": "error", "raison": "Aucune demande trouvée."})

app = Application(
    [LoanEvaluationComposite],
    tns='loan.composite',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    sys.exit(run_twisted([(WsgiApplication(app), b'LoanEvaluationService')], 8000))

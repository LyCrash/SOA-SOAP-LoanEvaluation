import sys, logging, json
from spyne import Application, rpc, ServiceBase, Unicode, Float
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted

logging.basicConfig(level=logging.INFO)

class CreditCheckService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def check_credit(ctx, data):
        """Receives JSON string and returns a JSON with credit score."""
        try:
            parsed = json.loads(data)
        except Exception as e:
            return json.dumps({"error": f"Invalid JSON: {e}"})

        revenu = float(parsed.get("revenu_mensuel", 0))
        depense = float(parsed.get("depenses_mensuelles", 0))
        montant = float(parsed.get("montant_pret", 1))
        ratio = (revenu - depense) / max(montant / 1000, 1)
        score = max(0, min(100, ratio * 20))
        result = json.dumps({"credit_score": score})
        print(f"[CC] Output: {result}")
        return result

app = Application(
    [CreditCheckService],
    tns='loan.services.credit',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    sys.exit(run_twisted([(WsgiApplication(app), b'CreditCheckService')], 8002))

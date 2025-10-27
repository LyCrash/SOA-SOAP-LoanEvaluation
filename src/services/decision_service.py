import sys, logging, json
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted

logging.basicConfig(level=logging.INFO)

class DecisionService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def make_decision(ctx, data):
        """Receives JSON data and returns decision JSON."""
        parsed = json.loads(data)
        score = parsed.get("credit_score", 0)
        value = parsed.get("property_value", 0)
        loan = parsed.get("loan_amount", 0)
        approved = score > 50 and value > loan * 0.8
        decision = {
            "approved": approved,
            "message": "Approved" if approved else "Rejected"
        }
        result = json.dumps(decision)
        print(f"[DS] Output: {result}")
        return result

app = Application(
    [DecisionService],
    tns='loan.services.decision',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    sys.exit(run_twisted([(WsgiApplication(app), b'DecisionService')], 8004))

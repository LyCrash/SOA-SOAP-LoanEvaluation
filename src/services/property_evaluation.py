import sys, logging, json, random
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted

logging.basicConfig(level=logging.INFO)

class PropertyEvaluationService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def evaluate_property(ctx, data):
        """Receives JSON data and returns property value estimation."""
        try:
            parsed = json.loads(data)
        except Exception:
            parsed = {"description": data}

        description = parsed.get("description", "")
        base_value = 150000 + len(description) * 20 + random.randint(-5000, 5000)
        result = json.dumps({"property_value": base_value})
        print(f"[PE] Output: {result}")
        return result

app = Application(
    [PropertyEvaluationService],
    tns='loan.services.property',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    sys.exit(run_twisted([(WsgiApplication(app), b'PropertyEvaluationService')], 8003))

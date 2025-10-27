import sys, logging, re, json
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted

logging.basicConfig(level=logging.INFO)

class InformationExtractionService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def extract_information(ctx, text):
        """Extract structured info from raw loan request text."""
        data = {}
        patterns = {
            "nom": r"Nom du Client:\s*(.*)",
            "adresse": r"Adresse:\s*(.*)",
            "email": r"Email:\s*(.*)",
            "telephone": r"Numéro de Téléphone:\s*(.*)",
            "montant_pret": r"Montant du Prêt Demandé:\s*([0-9]+)",
            "revenu_mensuel": r"Revenu Mensuel:\s*([0-9]+)",
            "depenses_mensuelles": r"Dépenses Mensuelles:\s*([0-9]+)",
            "description": r"Description de la Propriété:\s*(.*)"
        }
        for key, pat in patterns.items():
            match = re.search(pat, text)
            if match:
                data[key] = match.group(1).strip()

        result = json.dumps(data)
        print(f"[IE] Output: {result}")
        return result

app = Application(
    [InformationExtractionService],
    tns='loan.services.information',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    sys.exit(run_twisted([(WsgiApplication(app), b'InformationExtractionService')], 8001))

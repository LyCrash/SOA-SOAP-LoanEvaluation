import sys, logging, re, json
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted

logging.basicConfig(level=logging.INFO)

def clean_text(text: str) -> str:
    """Remove extra spaces and normalize common characters."""
    return re.sub(r'\s+', ' ', text.replace('\n', ' ')).strip()


class InformationExtractionService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def extract_information(ctx, text):
        """Extract structured info from a raw loan request text."""
        if not text or not isinstance(text, str):
            return json.dumps({"error": "Empty or invalid input."})

        text = clean_text(text)
        logging.info(f"[IE] Received request text: {text[:80]}...")

        # --- Regex patterns for basic NLP-like extraction ---
        patterns = {
            "nom": r"(?:Nom du Client|Nom)\s*:\s*([A-Za-zÀ-ÿ'\-\s]+)",
            "adresse": r"(?:Adresse|Adresse du Bien)\s*:\s*(.*?)(?=\s*(?:Email|Montant|$))",
            "email": r"(?:Email|Courriel)\s*:\s*([\w\.-]+@[\w\.-]+\.\w+)",
            "telephone": r"(?:Numéro de Téléphone|Téléphone)\s*:\s*([\d\+\-\s]+)",
            "montant_pret": r"(?:Montant du Prêt Demandé|Montant)\s*:\s*([\d\s]+)",
            "revenu_mensuel": r"(?:Revenu Mensuel|Revenu)\s*:\s*([\d\s]+)",
            "depenses_mensuelles": r"(?:Dépenses Mensuelles|Dépenses)\s*:\s*([\d\s]+)",
            "description": r"(?:Description de la Propriété|Description)\s*:\s*(.*)"
        }

        data = {}

        # --- Extract data using regex ---
        for key, pat in patterns.items():
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                value = clean_text(match.group(1))
                if key in ["montant_pret", "revenu_mensuel", "depenses_mensuelles"]:
                    try:
                        value = float(value.replace(" ", "").replace(",", "."))
                    except ValueError:
                        value = 0.0
                data[key] = value
            else:
                logging.warning(f"[IE] Missing value for: {key}")

        # --- Fill default values for missing keys ---
        defaults = {
            "nom": "Inconnu",
            "adresse": "Non spécifiée",
            "email": "unknown@email.com",
            "telephone": "N/A",
            "montant_pret": 0.0,
            "revenu_mensuel": 0.0,
            "depenses_mensuelles": 0.0,
            "description": "Aucune description fournie"
        }
        for key, default in defaults.items():
            data.setdefault(key, default)

        # --- Derived or enriched data ---
        # You could later add postal code extraction, or city inference here.
        data["texte_original"] = text[:500]  # Keep small snippet for reference

        result = json.dumps(data, indent=2, ensure_ascii=False)
        logging.info(f"[IE] Extracted info: {result}")
        return result


# --- SOAP Application Setup ---
app = Application(
    [InformationExtractionService],
    tns='loan.services.information',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    sys.exit(run_twisted([(WsgiApplication(app), b'InformationExtractionService')], 8001))

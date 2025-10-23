"""
Orchestrateur principal exposé en SOAP (Spyne).
Il offre deux opérations:
 - SubmitLoanRequest(text) -> retourne request_id
 - GetEvaluation(request_id) -> retourne texte structuré du résultat
Chaque méthode est commentée pour indiquer ses paramètres et retours.
"""

import logging
from spyne import ServiceBase, rpc, Application, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from .utils import new_request_id, read_db, write_db
from services.information_extraction import extract_information
from services.credit_check import check_credit
from services.property_evaluation import evaluate_property
from services.decision_service import decide
from services.notification import notify

logger = logging.getLogger("ServiceWebComposite")
logger.setLevel(logging.DEBUG)

class ServiceWebComposite(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def SubmitLoanRequest(ctx, text):
        """
        Reçoit la demande de prêt sous forme de texte libre.
        Paramètre:
          - text: string contenant la demande du client (texte libre)
        Retour:
          - request_id: identifiant unique de la demande (string)
        Comportement:
          - Extrait les informations, appelle les services internes (credit, property),
            prend la décision, stocke le résultat dans database.json, notifie (simulé).
        """
        logger.debug("Received SubmitLoanRequest")
        req_id = new_request_id()

        # 1) Extraction
        extracted = extract_information(text)
        logger.debug("Extracted: %s", extracted)

        # 2) Vérification de solvabilité
        credit = check_credit(extracted)
        logger.debug("Credit check: %s", credit)

        # 3) Évaluation propriété
        prop = evaluate_property(extracted)
        logger.debug("Property eval: %s", prop)

        # 4) Décision
        decision = decide(extracted, credit, prop)
        logger.debug("Decision: %s", decision)

        # 5) Stockage dans DB JSON
        db = read_db()
        db["requests"][req_id] = {
            "text": text,
            "extracted": extracted,
            "credit": credit,
            "property": prop,
            "decision": decision,
            "status": "DONE"
        }
        write_db(db)

        # 6) Notification simulée
        email = extracted.get("email") or "unknown"
        summary = f"Decision={decision.get('decision')}; details={decision.get('details')}"
        notify(req_id, email, summary)

        return req_id

    @rpc(Unicode, _returns=Unicode)
    def GetEvaluation(ctx, request_id):
        """
        Récupère le résultat de l'évaluation pour un request_id donné.
        Paramètres:
          - request_id: l'identifiant de la demande (string)
        Retour:
          - texte structuré (string) décrivant la décision et les détails
        """
        logger.debug("Received GetEvaluation for %s", request_id)
        db = read_db()
        req = db.get("requests", {}).get(request_id)
        if not req:
            return f"ERROR: request_id {request_id} not found."

        dec = req.get("decision", {})
        extracted = req.get("extracted", {})
        credit = req.get("credit", {})
        prop = req.get("property", {})

        # Construire un texte explicatif
        lines = [
            f"Request ID: {request_id}",
            f"Applicant: {extracted.get('name')}",
            f"Decision: {dec.get('decision')}",
            f"Decision details: {dec.get('details')}",
            f"Credit score: {credit.get('score')} (details: {credit.get('details')})",
            f"Debt ratio: {credit.get('debt_ratio')}",
            f"Estimated property value: {prop.get('estimated_value')}€ (compliant: {prop.get('compliant')})"
        ]
        return "\n".join(lines)


# Spyne application builder (exposed by main.py)
soap_app = Application([ServiceWebComposite],
                       tns="http://example.org/loan_evaluation",
                       in_protocol=Soap11(validator='lxml'),
                       out_protocol=Soap11())
wsgi_app = WsgiApplication(soap_app)

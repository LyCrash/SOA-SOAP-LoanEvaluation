"""
main.py

Launcher pour le Service Web Composite (SOAP).
Il importe l'Application Spyne exposée dans
composite_service/service_composite.py puis démarre Twisted.

Usage:
    python main.py
(Remarque: démarrez d'abord les services enfants sur leurs ports
8001-8004 pour que l'orchestrateur puisse les appeler.)
"""

import sys
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted

# importe le module composite (doit définir 'app' : spyne.Application)
from composite_service import service_composite

if __name__ == "__main__":
    # Crée le WSGI wrapper à partir de l'Application Spyne exposée
    wsgi_app = WsgiApplication(service_composite.app)

    apps = [
        (wsgi_app, b"LoanEvaluationService"),
    ]

    print("Starting Loan Evaluation Composite SOAP service on port 8000 ...")
    sys.exit(run_twisted(apps, 8000))

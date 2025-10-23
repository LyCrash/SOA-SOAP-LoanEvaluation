"""
Script principal qui lance le serveur Twisted/Spyne.
Le service SOAP est exposé sur un endpoint simple, avec WSDL disponible.
"""
import sys
from spyne.util.wsgi_wrapper import run_twisted
from composite_service.service_composite import wsgi_app

if __name__ == "__main__":
    # Lancer le serveur Twisted sur le port 8000.
    apps = [(wsgi_app, b"ServiceWebComposite"),]
    print("Starting SOAP server on port 8000 ...")
    sys.exit(run_twisted(apps, 8000))

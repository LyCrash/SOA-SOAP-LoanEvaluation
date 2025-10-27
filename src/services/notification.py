import sys, logging, json
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
from composite_service.utils import notify

logging.basicConfig(level=logging.INFO)

class NotificationService(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def send_notification(ctx, request_id, email, message):
        notify(request_id, email, message)
        return f"Notification logged for {email}"

app = Application(
    [NotificationService],
    tns='loan.services.notification',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    sys.exit(run_twisted([(WsgiApplication(app), b'NotificationService')], 8005))

import txaio
import json
import _thread
import time
from random import randint

from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

from autobahn.websocket.types import ConnectionDeny


complete_telemetry_transmitter1 = {}
complete_telemetry_transmitter1['name'] = 'dl2ic'
complete_telemetry_transmitter1['onair'] = False
complete_telemetry_transmitter1['node'] = {}
complete_telemetry_transmitter1['node']['name'] = 'db0xyz'
complete_telemetry_transmitter1['node']['ip'] = '44.3.4.5'
complete_telemetry_transmitter1['node']['port'] = 1234
complete_telemetry_transmitter1['node']['connected'] = True
complete_telemetry_transmitter1['node']['connected_since'] = '2018-04-23T18:25:43.511Z'
complete_telemetry_transmitter1['ntp'] = {}
complete_telemetry_transmitter1['ntp']['synced'] = True
complete_telemetry_transmitter1['ntp']['offset'] = 32,
complete_telemetry_transmitter1['ntp']['servers'] = [ '134.130.4.1', '1.2.3.4' ]
complete_telemetry_transmitter1['messages'] = {}
complete_telemetry_transmitter1['messages']['queued']= [13, 23, 33, 43, 53 ]
complete_telemetry_transmitter1['messages']['sent']= [ 14, 24, 34, 44, 54 ]
complete_telemetry_transmitter1['temperatures'] = {}
complete_telemetry_transmitter1['temperatures']['unit'] = 'C'
complete_telemetry_transmitter1['temperatures']['air_inlet'] = 12.2
complete_telemetry_transmitter1['temperatures']['air_outlet'] = 14.2
complete_telemetry_transmitter1['temperatures']['transmitter'] = 14.2
complete_telemetry_transmitter1['temperatures']['power_amplifier'] = 14.2
complete_telemetry_transmitter1['temperatures']['cpu'] = 14.2
complete_telemetry_transmitter1['temperatures']['power_supply'] = 14.2
complete_telemetry_transmitter1['power_supply'] = {}
complete_telemetry_transmitter1['power_supply']['on_battery'] = False
complete_telemetry_transmitter1['power_supply']['on_emergency_power'] = False
complete_telemetry_transmitter1['power_supply']['dc_input_voltage'] = 12.4
complete_telemetry_transmitter1['power_supply']['dc_input_current'] = 1.2
complete_telemetry_transmitter1['rf_output'] = {}
complete_telemetry_transmitter1['rf_output']['fwd'] = 12.2
complete_telemetry_transmitter1['rf_output']['refl'] = 1.2
complete_telemetry_transmitter1['rf_output']['vswr'] = 1.2
complete_telemetry_transmitter1['config'] = {}
complete_telemetry_transmitter1['config']['ip'] = '1.2.3.4'
complete_telemetry_transmitter1['config']['timeslots'] = [True, True, False, True, False, False, True, True, False, True, False, False, True, True, False, True, False, False]
complete_telemetry_transmitter1['config']['software'] = {}
complete_telemetry_transmitter1['config']['software']['name'] = 'Unipager'
complete_telemetry_transmitter1['config']['software']['version'] = '1.2.3'
complete_telemetry_transmitter1['hardware'] = {}
complete_telemetry_transmitter1['hardware']['platform'] = 'Raspberry Pi 3B+'

complete_telemetry_node1 = {}
complete_telemetry_node1['name'] = 'dl2ic'
complete_telemetry_node1['good_health'] = True
complete_telemetry_node1['microservices'] = {}
complete_telemetry_node1['microservices']['database'] = {}
complete_telemetry_node1['microservices']['database']['ok'] = True
complete_telemetry_node1['microservices']['database']['version'] = '1.2.3'

complete_telemetry_node1['microservices']['call'] = {}
complete_telemetry_node1['microservices']['call']['ok'] = True
complete_telemetry_node1['microservices']['call']['version'] = '1.2.3'

complete_telemetry_node1['microservices']['rubric'] = {}
complete_telemetry_node1['microservices']['rubric']['ok'] = True
complete_telemetry_node1['microservices']['rubric']['version'] = '1.2.3'

complete_telemetry_node1['microservices']['transmitter'] = {}
complete_telemetry_node1['microservices']['transmitter']['ok'] = True
complete_telemetry_node1['microservices']['transmitter']

complete_telemetry_node1['microservices']['cluster'] = {}
complete_telemetry_node1['microservices']['cluster']['ok'] = True
complete_telemetry_node1['microservices']['cluster']['version'] = '1.2.3'

complete_telemetry_node1['microservices']['telemetry'] = {}
complete_telemetry_node1['microservices']['telemetry']['ok'] = True
complete_telemetry_node1['microservices']['telemetry']['version'] = '1.2.3'

complete_telemetry_node1['microservices']['database-changes'] = {}
complete_telemetry_node1['microservices']['database-changes']['ok'] = True
complete_telemetry_node1['microservices']['database-changes']['version'] = '1.2.3'

complete_telemetry_node1['microservices']['statistics'] = {}
complete_telemetry_node1['microservices']['statistics']['ok'] = True
complete_telemetry_node1['microservices']['statistics']['version'] = '1.2.3'

complete_telemetry_node1['microservices']['rabbitmq'] = {}
complete_telemetry_node1['microservices']['rabbitmq']['ok'] = True
complete_telemetry_node1['microservices']['rabbitmq']['version'] = '1.2.3'

complete_telemetry_node1['microservices']['thirdparty'] = {}
complete_telemetry_node1['microservices']['thirdparty']['ok'] = True
complete_telemetry_node1['microservices']['thirdparty']['version'] = '1.2.3'

complete_telemetry_node1['connections'] = {}
complete_telemetry_node1['connections']['transmitters'] = 123
complete_telemetry_node1['connections']['third_party'] = 11
complete_telemetry_node1['connections']['websocket'] = 22

complete_telemetry_node1['system'] = {}
complete_telemetry_node1['system']['free_disk_space_mb'] = 1234
complete_telemetry_node1['system']['cpu_utilization'] = 0.2
complete_telemetry_node1['system']['is_hamcloud'] = False



class BaseService:
#   Simple base for our services.

    def __init__(self, proto):
        self.proto = proto
        self.is_closed = False

    def onOpen(self):
        pass

    def onClose(self, wasClean, code, reason):
        pass

    def onMessage(self, payload, isBinary):
        pass


class NodesService(BaseService):

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = "Echo 1 - {}".format(payload.decode('utf8'))
            print(msg)
            self.proto.sendMessage(msg.encode('utf8'))

    def onOpen(self):
        msg = json.dumps(complete_telemetry_node1)
#        print(msg)
        self.proto.sendMessage(msg.encode('utf8'))


    def sendtest(self):
        msg = "Testing"
        print(msg)
        self.proto.sendMessage(msg.encode('utf8'))

class TransmittersService(BaseService):

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = "Echo 2 - {}".format(payload.decode('utf8'))
            print(msg)
            self.proto.sendMessage(msg.encode('utf8'))

    def onOpen(self):
        msg = json.dumps(complete_telemetry_transmitter1)
#        print(msg)
        self.proto.sendMessage(msg.encode('utf8'))

class ServiceServerProtocol(WebSocketServerProtocol):

    SERVICEMAP = {'/nodes': NodesService,
                  '/transmitters': TransmittersService}

    def __init__(self):
        self.service = None
        self.is_closed = txaio.create_future()

    def onConnect(self, request):
        # request has all the information from the initial
        # WebSocket opening handshake ..
        print(request.peer)
        print(request.headers)
        print(request.host)
        print(request.path)
        print(request.params)
        print(request.version)
        print(request.origin)
        print(request.protocols)
        print(request.extensions)

        # We map to services based on path component of the URL the
        # WebSocket client requested. This is just an example. We could
        # use other information from request, such has HTTP headers,
        # WebSocket subprotocol, WebSocket origin etc etc
        ##
        if request.path in self.SERVICEMAP:
        # cls is the ServiceName defined in the SERVICEMAP dict
            cls = self.SERVICEMAP[request.path]
            self.service = cls(self)
        else:
            err = "No service under %s" % request.path
            print(err)
            raise ConnectionDeny(404, unicode(err))

    def onOpen(self):
        if self.service:
            self.service.onOpen()

    def onMessage(self, payload, isBinary):
        if self.service:
            self.service.onMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        if self.service:
            self.service.onClose(wasClean, code, reason)


if __name__ == '__main__':

    factory = WebSocketServerFactory(u"ws://0.0.0.0:9003")
    factory.protocol = ServiceServerProtocol
    listenWS(factory)
    reactor.run()

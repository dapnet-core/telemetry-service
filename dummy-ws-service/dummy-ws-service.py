import txaio
import json
import _thread
import time
from random import randint

from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

#from autobahn.twisted.resource import WebSocketResource

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
        self.factory.register(self)
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
    myreq = ''

    def __init__(self):
        self.service = None
        self.is_closed = txaio.create_future()

    def onConnect(self, request):
        # request has all the information from the initial
        # WebSocket opening handshake ..
#        print(request.peer)
#        print(request.headers)
#        print(request.host)
#        print(request.path)
#        print(request.params)
#        print(request.version)
#        print(request.origin)
#        print(request.protocols)
#        print(request.extensions)

        # We map to services based on path component of the URL the
        # WebSocket client requested. This is just an example. We could
        # use other information from request, such has HTTP headers,
        # WebSocket subprotocol, WebSocket origin etc etc
        ##
        if request.path in self.SERVICEMAP:
        # cls is the ServiceName defined in the SERVICEMAP dict
            cls = self.SERVICEMAP[request.path]
            self.service = cls(self)
            self.myreq = request.path
        else:
            err = "No service under %s" % request.path
            print(err)
            raise ConnectionDeny(404, unicode(err))

    def onOpen(self):
        self.factory.register(self, self.myreq)
        if self.service:
            self.service.onOpen()

    def onMessage(self, payload, isBinary):
        if self.service:
            self.service.onMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        self.factory.unregister(self)
        if self.service:
            self.service.onClose(wasClean, code, reason)


class DAPNETFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super(DAPNETFactory, self).__init__(*args, **kwargs)
        self.clients = {}

    def register(self, client, endpoint):
        # Add client to list of managed connections.
        self.clients[client.peer] = {"object": client, "endpoint": endpoint}

    def unregister(self, client):
        # Remove client from list of managed connections.
        self.clients.pop(client.peer)

    def send2client(self, SelectedEndpoint, message):
        for key, value in self.clients.items():
            thisClient = value["object"]
            thisEndpoint = value["endpoint"]
            if thisEndpoint == SelectedEndpoint:
                thisClient.sendMessage(message.encode('utf8'))

def node_update_all(threadName, delay, myfactory):
    while 1:
        complete_telemetry_node1['good_health'] = (randint(0, 50) > 40)

        complete_telemetry_node1['microservices']['database']['ok'] = (randint(0, 50) > 40)
        complete_telemetry_node1['microservices']['call']['ok'] = (randint(0, 50) > 40)
        complete_telemetry_node1['microservices']['rubric']['ok'] = (randint(0, 50) > 40)
        complete_telemetry_node1['microservices']['transmitter']['ok'] = (randint(0, 50) > 40)
        complete_telemetry_node1['microservices']['cluster']['ok'] = (randint(0, 50) > 40)
        complete_telemetry_node1['microservices']['telemetry']['ok'] = (randint(0, 50) > 40)
        complete_telemetry_node1['microservices']['database-changes']['ok'] = (randint(0, 50) > 40)
        complete_telemetry_node1['microservices']['statistics']['ok'] = (randint(0, 50) > 40)
        complete_telemetry_node1['microservices']['rabbitmq']['ok'] = (randint(0, 50) > 40)
        complete_telemetry_node1['microservices']['thirdparty']['ok'] = (randint(0, 50) > 40)

        complete_telemetry_node1['connections']['transmitters'] = randint(0, 300)
        complete_telemetry_node1['connections']['third_party'] = randint(0, 30)
        complete_telemetry_node1['connections']['websocket'] = randint(1, 30)

        complete_telemetry_node1['system']['free_disk_space_mb'] = randint(0, 3000)
        complete_telemetry_node1['system']['cpu_utilization'] = randint(0, 100) / 100
        complete_telemetry_node1['system']['is_hamcloud'] = (randint(0, 50) > 40)


        msg = json.dumps(complete_telemetry_node1)
        myfactory.send2client('/nodes', msg)
        time.sleep (delay)

def transmitter_update_ntp(threadName, delay, myfactory):
    while 1:
        complete_telemetry_transmitter1['ntp']['synced'] = (randint(0, 50) > 40)
        update_data = {}
        update_data['name'] = complete_telemetry_transmitter1['name']

        if complete_telemetry_transmitter1['ntp']['synced']:
            complete_telemetry_transmitter1['ntp']['offset'] = randint(0, 2000)
            update_data['ntp'] = complete_telemetry_transmitter1['ntp']
        else:
            update_data['ntp'] = {}
            update_data['ntp']['synced'] = False

        msg = json.dumps(update_data)
        myfactory.send2client('/transmitters', msg)
        time.sleep (delay)

def transmitter_update_rf_output(threadName, delay, myfactory):
    while 1:
        complete_telemetry_transmitter1['rf_output']['fwd'] = randint(5, 2000) / 10
        complete_telemetry_transmitter1['rf_output']['refl'] = randint(0, 100) / 10
        complete_telemetry_transmitter1['rf_output']['vswr'] = randint(10, 30) / 10

        update_data = {}
        update_data['name'] = complete_telemetry_transmitter1['name']
        update_data['rf_output'] = complete_telemetry_transmitter1['rf_output']


        msg = json.dumps(update_data)
        myfactory.send2client('/transmitters', msg)
        time.sleep (delay)


def transmitter_update_power_supply(threadName, delay, myfactory):
    while 1:
        complete_telemetry_transmitter1['power_supply']['on_battery'] = (randint(0, 10) > 8)
        complete_telemetry_transmitter1['power_supply']['on_emergency_power'] = (randint(0, 10) > 8)
        complete_telemetry_transmitter1['power_supply']['dc_input_voltage'] = randint(100, 150) / 10
        complete_telemetry_transmitter1['power_supply']['dc_input_current'] = randint(5, 100) / 10

        update_data = {}
        update_data['name'] = complete_telemetry_transmitter1['name']
        update_data['power_supply'] = complete_telemetry_transmitter1['power_supply']

        msg = json.dumps(update_data)
        myfactory.send2client('/transmitters', msg)
        time.sleep (delay)

def transmitter_update_temp(threadName, delay, myfactory):
    while 1:
        complete_telemetry_transmitter1['temperatures']['air_inlet'] = randint(-100, 800) / 10
        complete_telemetry_transmitter1['temperatures']['air_outlet'] = randint(-100, 800) / 10
        complete_telemetry_transmitter1['temperatures']['transmitter'] = randint(-100, 800) / 10
        complete_telemetry_transmitter1['temperatures']['power_amplifier'] = randint(-100, 800) / 10
        complete_telemetry_transmitter1['temperatures']['cpu'] = randint(-100, 800) / 10
        complete_telemetry_transmitter1['temperatures']['power_supply'] = randint(-100, 800) / 10

        update_data = {}
        update_data['name'] = complete_telemetry_transmitter1['name']
        update_data['temperatures'] = complete_telemetry_transmitter1['temperatures']

        msg = json.dumps(update_data)
        myfactory.send2client('/transmitters', msg)
        time.sleep (delay)

def transmitter_update_messages(threadName, delay, myfactory):
    while 1:
        complete_telemetry_transmitter1['messages']['queued']= [randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 100), ]
        complete_telemetry_transmitter1['messages']['sent']= [randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 100), ]

        update_data = {}
        update_data['name'] = complete_telemetry_transmitter1['name']
        update_data['messages'] = complete_telemetry_transmitter1['messages']

        msg = json.dumps(update_data)
        myfactory.send2client('/transmitters', msg)
        time.sleep (delay)

def transmitter_update_onair(threadName, delay, myfactory):
    while 1:
        complete_telemetry_transmitter1['onair'] = (randint(0, 10) > 7)
        update_data = {}
        update_data['name'] = complete_telemetry_transmitter1['name']
        update_data['onair'] = complete_telemetry_transmitter1['onair']

        msg = json.dumps(update_data)
        myfactory.send2client('/transmitters', msg)
        time.sleep (delay)

if __name__ == '__main__':

    factory = DAPNETFactory(u"ws://0.0.0.0:9001")
    factory.protocol = ServiceServerProtocol
    listenWS(factory)
    _thread.start_new_thread( node_update_all, ("Thread-node_update_all", 10, factory, ) )
    _thread.start_new_thread( transmitter_update_ntp, ("Thread-transmitter_update_ntp", 10, factory, ) )
    _thread.start_new_thread( transmitter_update_rf_output, ("Thread-transmitter_update_rf_output", 2, factory, ) )
    _thread.start_new_thread( transmitter_update_power_supply, ("Thread-transmitter_update_power_supply", 2, factory, ) )
    _thread.start_new_thread( transmitter_update_temp, ("Thread-transmitter_update_temp", 8, factory, ) )
    _thread.start_new_thread( transmitter_update_messages, ("Thread-transmitter_update_messages", 4, factory, ) )
    _thread.start_new_thread( transmitter_update_onair, ("Thread-transmitter_update_onair", 4, factory, ) )
    reactor.run()

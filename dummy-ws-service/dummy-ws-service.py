from websocket_server import WebsocketServer
import json
import _thread
import time
from random import randint

PORT = 9001
Clients = {}
user = 'test'
password = 'test1234'

complete_telemetry_1 = {}
complete_telemetry_1['type'] = 'telemetry'
complete_telemetry_1['name'] = 'dl2ic'
complete_telemetry_1['onair'] = False
complete_telemetry_1['node'] = {}
complete_telemetry_1['node']['name'] = 'db0xyz'
complete_telemetry_1['node']['ip'] = '44.3.4.5'
complete_telemetry_1['node']['port'] = 1234
complete_telemetry_1['node']['connected'] = True
complete_telemetry_1['node']['connected_since'] = '2018-04-23T18:25:43.511Z'
complete_telemetry_1['ntp'] = {}
complete_telemetry_1['ntp']['synced'] = True
complete_telemetry_1['ntp']['offset'] = 32,
complete_telemetry_1['ntp']['servers'] = [ '134.130.4.1', '1.2.3.4' ]
complete_telemetry_1['messages'] = {}
complete_telemetry_1['messages']['queued']= [13, 23, 33, 43, 53 ]
complete_telemetry_1['messages']['sent']= [ 14, 24, 34, 44, 54 ]
complete_telemetry_1['temperatures'] = {}
complete_telemetry_1['temperatures']['unit'] = 'C'
complete_telemetry_1['temperatures']['air_inlet'] = 12.2
complete_telemetry_1['temperatures']['air_outlet'] = 14.2
complete_telemetry_1['temperatures']['transmitter'] = 14.2
complete_telemetry_1['temperatures']['power_amplifier'] = 14.2
complete_telemetry_1['temperatures']['cpu'] = 14.2
complete_telemetry_1['temperatures']['power_supply'] = 14.2



def send_all_public(threadName, delay, server):
    while 1:
        server.send_message_to_all(json.dumps(complete_telemetry_1))
        time.sleep (delay)
#        print ('Send public message from %s' % (threadName))

def send_temp_public(threadName, delay, server):
    while 1:
        complete_telemetry_1['temperatures']['air_inlet'] = randint(-100, 800) / 10
        complete_telemetry_1['temperatures']['air_outlet'] = randint(-100, 800) / 10
        complete_telemetry_1['temperatures']['transmitter'] = randint(-100, 800) / 10
        complete_telemetry_1['temperatures']['power_amplifier'] = randint(-100, 800) / 10
        complete_telemetry_1['temperatures']['cpu'] = randint(-100, 800) / 10
        complete_telemetry_1['temperatures']['power_supply'] = randint(-100, 800) / 10

        update_data = {}
        update_data['name'] = complete_telemetry_1['name']
        update_data['type'] = complete_telemetry_1['type']
        update_data['temperatures'] = complete_telemetry_1['temperatures']

        server.send_message_to_all(json.dumps(update_data))
        time.sleep (delay)
#        print ('Send public message from %s' % (threadName))

def send_tx_public(threadName, delay, server):
    while 1:
        complete_telemetry_1['onair'] = (randint(0, 10) > 7)
        update_data = {}
        update_data['name'] = complete_telemetry_1['name']
        update_data['type'] = complete_telemetry_1['type']
        update_data['onair'] = complete_telemetry_1['onair']

        server.send_message_to_all(json.dumps(update_data))
        time.sleep (delay)
#        print ('Send public message from %s' % (threadName))

def send_test_private(threadName, delay, server):
    data = {}
    data['test'] = '5678'
    data['public'] = False
    while 1:
        for clientid, clientdata in Clients.items():
            if clientdata['auth']:
                server.send_message(clientdata['client'],json.dumps(data))
        time.sleep (delay)
#        print ('Send private message from %s' % (threadName))


# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
# New connection, client is not authenticated
    Clients[client['id']] = {}
    Clients[client['id']]['auth'] = False
    Clients[client['id']]['client'] = client
    server.send_message_to_all(json.dumps(complete_telemetry_1))


# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])
# Remove client ID from hash
    del Clients[client['id']]


# Called when a client sends a message
def message_received(client, server, message):
    print("Client(%d) said: %s" % (client['id'], message))
    message_json = json.loads(message)
    if 'Authenticate' in message_json:
        answer = {}
        if message_json['Authenticate']['user'] == user and  message_json['Authenticate']['password'] == password:
            Clients[client['id']]['auth'] = True
            answer['Authenticated'] = True
            server.send_message(client,json.dumps(answer))

# Initial complete dump of telemetry data
            server.send_message(client,json.dumps(complete_telemetry_1))
        else:
            Clients[client['id']]['auth'] = False
            answer['Authenticated'] = False
            server.send_message(client,json.dumps(answer))

server = WebsocketServer(PORT, host='0.0.0.0')
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)

_thread.start_new_thread( send_all_public, ("Thread-all_public", 30, server, ) )
_thread.start_new_thread( send_temp_public, ("Thread-temp_public", 10, server, ) )
_thread.start_new_thread( send_tx_public, ("Thread-tx_public", 2, server, ) )

#_thread.start_new_thread( send_test_private, ("Thread-test_private", 3, server, ) )

server.run_forever()

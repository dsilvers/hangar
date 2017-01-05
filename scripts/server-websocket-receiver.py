import pusherclient
import time
import sys
import json
from heater.models import Switch, TemperatureProbe

# Add a logging handler so we can see the raw communication data
import logging
root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
root.addHandler(ch)



def receive_temperature_log(data):
    data = json.loads(data)

    status = Status()
    status.engine_switch = False if data['engine_switch'] == "0" else True
    status.cabin_switch = False if data['cabin_switch'] == "0" else True
    status.ambient_temp = data['ambient_temp']
    status.engine_temp = data['engine_temp']
    status.cabin_temp = data['cabin_temp']
    status.save()


def receive_switch_log(data):
    data = json.loads(data)

    


def receive_setup_request(data):
    pusher_client.trigger('hangar-status', 'setup-response', {
        'switches': Switch.objects.all(),
        'probes': TemperatureProbe.objects.all(),
    })



# We can't subscribe until we've connected, so we use a callback handler
# to subscribe when able
def connect_handler(data):
    channel = pusher.subscribe('hangar-status')
    channel.bind('temperature-log', receive_temperature_log)
    channel.bind('switch-log', receive_switch_log)
    channel.bind('setup-request', receive_setup_request)

pusher = pusherclient.Pusher('44ff3ecdb4e3aeae676f')
pusher.connection.bind('pusher:connection_established', connect_handler)
pusher.connect()

while True:
    # Do other things in the meantime here...
    time.sleep(1)
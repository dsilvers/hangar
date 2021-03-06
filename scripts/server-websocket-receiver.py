import pusher
import pusherclient
import time
import sys
import json
from urllib2 import urlopen
from metar import Metar

from django.conf import settings
from django.utils import timezone
from heater.models import Switch, TemperatureProbe, TemperatureData
from heater.utils import bool_to_switch_state

# Add a logging handler so we can see the raw communication data
import logging
root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
root.addHandler(ch)

pusher_client = pusher.Pusher(
    app_id = settings.PUSHER_APP_ID,
    key = settings.PUSHER_APP_KEY,
    secret = settings.PUSHER_APP_SECRET,
)


def send_airport_metar():
    if not settings.AIRPORT:
        logging.info("Airport ID not set, unable to grab METAR")
        return

    BASE_URL = "http://tgftp.nws.noaa.gov/data/observations/metar/stations"
    url = "%s/%s.TXT" % (BASE_URL, settings.AIRPORT)

    try:
        urlh = urlopen(url)
        for line in urlh:
            if line.startswith(settings.AIRPORT):
                obs = Metar.Metar(line)
                break
    except Metar.ParserError:
        logging.info("Unable to parse METAR")
        return
    except:
        logging.info("Unable to parse METAR")
        return

    temperature = obs.temp.string().replace(" C", "")

    probe_data = []
    probe_data.append({
        'name': settings.AIRPORT,
        'serial': settings.AIRPORT,
        'temperature':  temperature,
    })
    logging.info("Probe {} on {} has temperature of {}'C".format(
        settings.AIRPORT,
        settings.AIRPORT,
        temperature,
    ))

    pusher_client.trigger(['hangar-status'], 'temperature-log', probe_data)


def receive_temperature_log(data):
    data = json.loads(data)
    logging.info("Temperature Log received: {}".format(data))

    for probe_data in data:
        try:
            probe = TemperatureProbe.objects.filter(serial=probe_data['serial']).get()
        except TemperatureProbe.DoesNotExist:
            probe = False
            logging.info("Probe not found: {}".format(data['serial']))

        if probe:
            probe_temp = TemperatureData()
            probe_temp.probe = probe
            probe_temp.temperature = probe_data['temperature']
            probe_temp.save()

            probe.current_temperature = probe_data['temperature']
            probe.current_temperature_timestamp = timezone.now()
            probe.save()

            logging.info("Probe temperature log: {} ({}) is {}".format(
                probe.name,
                probe.serial,
                probe_data['temperature'],
            ))


def receive_switch_log(data):
    data = json.loads(data)
    logging.info("Switch Log received: {}".format(data))

    try:
        switch = Switch.objects.filter(name=data['name']).get()
    except Switch.DoesNotExist:
        switch = False
        logging.info("Switch not found: {}".format(data['name']))

    if switch:
        switch.set_state(data['state'])
        logging.info("Switch state set to: {} | {}".format(
            data['state'],
            bool_to_switch_state(data['state']),
        ))


def receive_setup_request(data):
    switches = []
    probes = []

    for switch in Switch.objects.all():
        switches.append({
            'name': switch.name,
            'pin': switch.pin,
            'state': switch.state,
        })

    for probe in TemperatureProbe.objects.all():
        probes.append({
            'name': probe.name,
            'serial': probe.serial,
        })
    
    pusher_client.trigger(['hangar-status'], 'setup-response', {
        'switches': switches,
        'probes': probes,
    })
    logging.info("Setup request received and responded. {} switches, {} probes.".format(
        len(switches),
        len(probes),
    ))


# We can't subscribe until we've connected, so we use a callback handler
# to subscribe when able
def connect_handler(data):
    channel = pusher.subscribe('hangar-status')
    channel.bind('temperature-log', receive_temperature_log)
    channel.bind('switch-log', receive_switch_log)
    channel.bind('setup-request', receive_setup_request)
    logging.info("Connected to pusher")
    receive_setup_request(None)


pusher = pusherclient.Pusher(settings.PUSHER_APP_KEY)
pusher.connection.bind('pusher:connection_established', connect_handler)

def run():
    pusher.connect()
    while True:
        # Do other things in the meantime here...
        time.sleep(10)
        # Grab a METAR
        send_airport_metar()
        time.sleep(20*60)


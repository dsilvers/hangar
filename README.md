## Hangar Control

Hangar relay/switch control and temperature monitoring. Provides UI and logging to database.


## Install

`sudo apt-get install build-essential libssl-dev libffi-dev python-dev
pip install -r requirements.txt

sudo ln -s hangar_nginx.conf /etc/nginx/sites-enabled/
sudo /etc/init.d/nginx restart

cp hangar/settings_local_example.py hangar/settings_local.py
<configure settings_local.py>


`


## Backend Client

To run the backend client in test mode, run:

`./manage.py runscript server-websocket-receiver`
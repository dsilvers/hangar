from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from heater.models import TemperatureProbe, Switch

import pusher


class StatusPage(View):
    def get(self, request):
        return render(request, "index.html", { 
            'PUSHER_APP_KEY': settings.PUSHER_APP_KEY,
            'probes': TemperatureProbe.objects.all(),
            'switches': Switch.objects.all(),
        })



@login_required
def control_switch(request, name, state):
    pusher_client = pusher.Pusher(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_APP_KEY,
        secret=settings.PUSHER_APP_SECRET,
    )

    try:
        switch = Switch.objects.filter(name=name).get()
    except State.DoesNotExist():
        return HttpResponse("No switch by that name, son.")

    if state == "1":
        state = True
    elif state == "0":
        state = False
    else:
        state = None

    pusher_client.trigger('hangar-status', 'switches', {
        'name': switch.name,
        'pin': switch.pin,
        'state': state,
    })

    return HttpResponse("OK")
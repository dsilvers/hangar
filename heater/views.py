from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import View

from heater.models import TemperatureProbe, Switch

import pusher


class StatusPage(View):
    template_name = "index.html"

    def get(self, request):
        return render(request, self.template_name, { 
            'PUSHER_APP_KEY': settings.PUSHER_APP_KEY,
            'probes': TemperatureProbe.objects.all(),
            'switches': Switch.objects.all(),
        })


def control_switch(request, name, status):

    try:
        state = State.objects.filter(name=name).get()
    except State.DoesNotExist():
        return HttpResponse("No switch by that name, son.")


    pusher_client = pusher.Pusher(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_APP_KEY,
        secret=settings.PUSHER_APP_SECRET,
        ssl=True
    )

    pusher_client.trigger('hangar-status', 'switch-control', {
        'name': name,
        'status': status,
    })

    state.state = False if status == "0" else True
    state.save()

    return HttpResponse("OK")
from django.contrib import admin
from heater.models import TemperatureProbe, TemperatureData, Switch, SwitchData

admin.site.register(TemperatureProbe)
admin.site.register(Switch)
admin.site.register(TemperatureData)
admin.site.register(SwitchData)
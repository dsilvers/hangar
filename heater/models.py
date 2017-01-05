from __future__ import unicode_literals

from django.db import models
from heater.utils import bool_to_switch_state


class Switch(models.Model):
    name = models.CharField(max_length=32, unique=True)
    pin = models.CharField(max_length=32)
    state = models.BooleanField(default=False)
    probe = models.ForeignKey("TemperatureProbe", blank=True, null=True)
    last_change = models.DateTimeField(auto_now=True)
    sequence = models.IntegerField(default=0)

    def __unicode__(self):
        return "{} ({})".format(self.name, bool_to_switch_state(self.state))

    class Meta:
        ordering = ['sequence']


class SwitchData(models.Model):
    switch = models.ForeignKey(Switch)
    timestamp = models.DateTimeField(auto_now_add=True)
    state = models.BooleanField(default=False)

    def __unicode__(self):
        return "{} ({})".format(
            self.switch.name, 
            bool_to_switch_state(self.state),
        )
    
    class Meta:
        ordering = ['-timestamp']
        get_latest_by = "timestamp"


class TemperatureData(models.Model):
    probe = models.ForeignKey("TemperatureProbe")
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.DecimalField(max_digits=6, decimal_places=3)    

    def __unicode__(self):
        return "{} - {}".format(self.probe.name, self.temperature)

    class Meta:
        ordering = ['-timestamp']
        get_latest_by = "timestamp"


class TemperatureProbe(models.Model):
    name = models.CharField(max_length=32)
    serial = models.CharField(max_length=32, unique=True)
    sequence = models.IntegerField(default=0)

    @property
    def temperature(self):
        try:
            return TemperatureData.objects.filter(probe=self).latest().temperature
        except TemperatureData.DoesNotExist:
            return None

    def __unicode__(self):
        return "{} ({})".format(self.name, self.serial)

    class Meta:
        ordering = ['sequence']

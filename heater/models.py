from __future__ import unicode_literals

from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from heater.utils import bool_to_switch_state


class Switch(models.Model):
    name = models.CharField(max_length=32, unique=True)
    pin = models.CharField(max_length=32)
    probe = models.ForeignKey("TemperatureProbe", blank=True, null=True)
    last_change = models.DateTimeField(auto_now=True)
    sequence = models.IntegerField(default=0)

    def __unicode__(self):
        return "{} ({})".format(self.name, bool_to_switch_state(self.state))

    @property
    def state(self):
        try:
            return SwitchData.objects.filter(switch=self).latest().state
        except SwitchData.DoesNotExist:
            return None

    def set_state(self, state):
        data = SwitchData()
        data.switch = self
        data.state = state
        data.save()

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
            t = TemperatureData.objects.filter(probe=self).latest()
        except TemperatureData.DoesNotExist:
            return None

        if timezone.now() - t.timestamp > settings.TEMPERATURE_STALENESS:
            return False

        return t.temperature

    @property
    def temperature_c(self):
        return self.temperature

    @property
    def temperature_f(self):
        return (self.temperature * Decimal(1.8)) + Decimal(32.0)

    def __unicode__(self):
        return "{} ({})".format(self.name, self.serial)

    class Meta:
        ordering = ['sequence']

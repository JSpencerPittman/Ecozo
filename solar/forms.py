from django import forms


class SolarForm(forms.Form):
    # Location Data
    latitude = forms.FloatField()
    longitude = forms.FloatField()

    # Solar Panel Specs
    capacity = forms.FloatField()
    efficiency = forms.FloatField()
    area = forms.FloatField()

    # Solar Irradiation Exposure
    intensity = forms.FloatField()
    duration = forms.FloatField()

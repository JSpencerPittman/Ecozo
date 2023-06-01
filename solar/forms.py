from django import forms


class SolarPanelForm(forms.Form):
    # Solar Panel Specs
    efficiency = forms.FloatField()
    area = forms.FloatField()
    performance_ratio = forms.FloatField()

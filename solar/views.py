from django.shortcuts import render, redirect
from solar.forms import SolarForm
from PowerEstimation import PowerEstimation, GeoLocation, SolarPanel, SolarExposure


def solar(request):
    context = dict()
    context['form'] = SolarForm()

    if request.method == 'POST':
        form = SolarForm(request.POST)
        if form.is_valid():
            solar_data = form.cleaned_data
            loc = GeoLocation(lat=solar_data['latitude'], lon=solar_data['longitude'])
            sp = SolarPanel(cap=solar_data['capacity'], eff=solar_data['efficiency'], area=solar_data['area'])
            exp = SolarExposure(irr=solar_data['intensity'], dur=solar_data['duration'])
            pow_est = PowerEstimation(loc, sp, exp)
            context['location'] = loc
            context['solar_panel'] = sp
            context['exposure'] = exp
            context['pow'] = pow_est.power_generated()

    print(context)
    print(context['form']['area'])
    return render(request, 'solar.html', context)
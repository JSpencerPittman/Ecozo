from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from solar.modellinks.charlie import charlie_link
from solar.modellinks.delta import delta_link
import json
from geopy.geocoders import Nominatim


@csrf_exempt
@never_cache
def solar(request):
    context = dict()
    loc_in_session = 'location' in request.session
    sp_in_session = 'solar_panel' in request.session

    if loc_in_session:
        context['location'] = request.session['location']
    else:
        context['location'] = {
            'latitude': '---',
            'longitude': '---',
            'city': '---',
            'country': '---'
        }

    if sp_in_session:
        context['solar_panel'] = request.session['solar_panel']

    if loc_in_session and sp_in_session:
        if not request.session['solar_power_satisfied']:
            charlie_results = charlie_link(request)
            delta_results = delta_link(request)

            results = dict(
                hour=delta_results['hour'],
                day=delta_results['day'],
                five_days=delta_results['five_days'],
                month=charlie_results['month'],
                year=charlie_results['year']
            )
            print(results)

            request.session['solar_power'] = results
            request.session['solar_power_satisfied'] = True

        context['solar_power'] = request.session['solar_power']

    else:
        context['solar_power'] = {
            'hour': '---',
            'day': '---',
            'five_days': '---',
            'month': '---',
            'year': '---',
        }

    return render(request, 'solar.html', context)


@csrf_exempt
def solar_geo(request):
    if request.method != 'POST':
        redirect('/solar')

    data = json.loads(request.body)

    latitude = data["latitude"]
    longitude = data["longitude"]

    locator = Nominatim(user_agent="myGeocoder")
    coordinates = f"{latitude}, {longitude}"
    location = locator.reverse(coordinates, timeout=10000)

    city = location.raw['address']['city']
    country = location.raw['address']['country']

    data['city'] = city
    data['country'] = country

    request.session['location'] = data

    return redirect('/solar')


@csrf_exempt
def solar_panel(request):
    if request.method != 'POST':
        return redirect('/solar')

    data = json.loads(request.body)

    if float(data['efficiency']) > 1:
        data['efficiency'] = float(data['efficiency']) / 100
    if float(data['pr']) > 1:
        data['pr'] = float(data['pr']) / 100

    request.session['solar_panel'] = data

    request.session['solar_power_satisfied'] = False

    return redirect('/solar')

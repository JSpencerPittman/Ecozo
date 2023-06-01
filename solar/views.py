from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from solar.modellinks.alpha import alpha_link
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
        if not request.session['power_satisfied']:
            request.session['power'] = alpha_link(request)
            request.session['power_satisfied'] = True

        context['power'] = request.session['power']

    else:
        context['power'] = {
            'hour': '---',
            'day': '---',
            'five_days': '---',
            'month': '---',
            'year': '---',
            'satisfied': 0
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
    location = locator.reverse(coordinates)

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

    request.session['power_satisfied'] = False

    return redirect('/solar')

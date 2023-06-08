from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from wind.modellinks.aeolus import aeolus_link
from geopy.geocoders import Nominatim
import json


@csrf_exempt
@never_cache
def wind(request):
    context = dict()
    loc_in_session = 'location' in request.session
    wt_in_session = 'wind_turbine' in request.session

    if loc_in_session:
        context['location'] = request.session['location']
    else:
        context['location'] = {
            'latitude': '---',
            'longitude': '---',
            'city': '---',
            'country': '---'
        }

    if wt_in_session:
        context['wind_turbine'] = request.session['wind_turbine']

    if loc_in_session and wt_in_session:
        if not request.session['wind_power_satisfied']:
            aeolus_results = aeolus_link(request)

            request.session['wind_power'] = aeolus_results
            request.session['wind_power_satisfied'] = True

        context['wind_power'] = request.session['wind_power']

    else:
        context['wind_power'] = {
            'hour': '---',
            'day': '---',
            'five_days': '---',
            'month': '---',
            'year': '---',
            'satisfied': 0
        }

    return render(request, 'wind.html', context)


@csrf_exempt
def wind_geo(request):
    if request.method != 'POST':
        redirect('/wind')

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

    return redirect('/wind')


@csrf_exempt
def wind_turbine(request):
    if request.method != 'POST':
        return redirect('/wind')

    data = json.loads(request.body)

    if float(data['efficiency']) > 1:
        data['efficiency'] = float(data['efficiency']) / 100

    request.session['wind_turbine'] = data

    request.session['wind_power_satisfied'] = False

    return redirect('/wind')

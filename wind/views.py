from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from wind.modellinks.aeolus import aeolus_link
from wind.modellinks.boreas import boreas_link
from geopy.geocoders import Nominatim
from util.geolocate import geocode
import json


@csrf_exempt
@never_cache
def wind(request):
    context = dict()
    loc_in_session = 'location' in request.session
    wt_in_session = 'wind_turbine' in request.session

    if loc_in_session:
        context['location'] = request.session['location']
        print(request.session['location'])

    if wt_in_session:
        context['wind_turbine'] = request.session['wind_turbine']

    if loc_in_session and wt_in_session:
        if not request.session['wind_power_satisfied']:
            aeolus_results = aeolus_link(request)
            boreas_results = boreas_link(request)

            results = dict(
                hour=boreas_results['hour'],
                day=boreas_results['day'],
                five_days=boreas_results['five_days'],
                month=aeolus_results['month'],
                year=aeolus_results['year']
            )

            request.session['wind_power'] = results
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

    coordinates = True
    address = True

    # Find out what information we do have
    if data['latitude'] == '' or data['longitude'] == '':
        coordinates = False
    if data['city'] == '' or data['state'] == '' or data['zipcode'] == '':
        address = False

    print(coordinates)
    print(address)

    # Don't have enough information
    if not coordinates and not address:
        return redirect('/wind')

    # Resolved the coordinates
    if not coordinates and address:
        lat, lon = geocode(data['city'], data['state'], data['zipcode'])

        data['latitude'] = float(lat)
        data['longitude'] = float(lon)
    else:
        lat, lon = data['latitude'], data['longitude']

    # Resolve the address
    if not address:
        locator = Nominatim(user_agent="myGeocoder")
        coordinates = f"{lat}, {lon}"
        location = locator.reverse(coordinates, timeout=10000)

        city = location.raw['address']['city']
        state = location.raw['address']['state']
        zipcode = location.raw['address']['postcode']

        data['city'] = city
        data['state'] = state
        data['zipcode'] = zipcode

    request.session['location'] = data
    print(request.session['location'])

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

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from solar.modellinks.charlie import charlie_link
from solar.modellinks.delta import delta_link
import json
from geopy.geocoders import Nominatim
from util.geolocate import geocode


@csrf_exempt
@never_cache
def solar(request):
    context = dict()
    loc_in_session = 'location' in request.session
    sp_in_session = 'solar_panel' in request.session

    if loc_in_session:
        context['location'] = request.session['location']

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

    coordinates = True
    address = True

    # Find out what information we do have
    if data['latitude'] == '' or data['longitude'] == '':
        coordinates = False
    if data['city'] == '' or data['state'] == '' or data['zipcode'] == '':
        address = False

    # Don't have enough information
    if not coordinates and not address:
        return redirect('/solar')

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

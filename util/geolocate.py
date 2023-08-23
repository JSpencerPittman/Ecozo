import requests


def geocode(city, state, zipcode):
    base_url = "https://geocode.maps.co/search?q="
    search_string = "+".join([city, state, zipcode]).replace(' ', '+') + '+US'
    url = base_url + search_string

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        raise Exception("GeocodeError: geocode API couldn't be accessed!")

    if not data:
        return 0, 0

    lat, lon = data[0]['lat'], data[0]['lon']

    return lat, lon

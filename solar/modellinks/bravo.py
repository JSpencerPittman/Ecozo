from irradiance.models.bravo import Bravo
from irradiance.models.model import SolarPanel
from DataManager.OpenWeather import OpenWeatherAPI


def bravo_link(request):
    latitude = request.session['location']['latitude']
    longitude = request.session['location']['longitude']

    area = request.session['solar_panel']['area']
    efficiency = request.session['solar_panel']['efficiency']
    pr = request.session['solar_panel']['pr']
    capacity = request.session['solar_panel']['capacity']

    solar_panel = SolarPanel(efficiency, area, pr, capacity)

    ow_api = OpenWeatherAPI()

    ow_api.calibrate(latitude, longitude)
    ow_api.download()
    ow_df = ow_api.get_dataframe()

    bravo_model = Bravo(solar_panel)
    bravo_model.predict(ow_df, latitude, longitude)

    results = dict(
        hour=bravo_model.hour(),
        day=bravo_model.day(),
        five_days=bravo_model.five_days(),
        month=bravo_model.month(),
        year=bravo_model.year()
    )

    for key, val in results.items():
        results[key] = round(val, 2)

    return results

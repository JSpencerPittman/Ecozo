from irradiance.models.delta import Delta
from irradiance.models.model import SolarPanel
from DataManager.OpenWeather import OpenWeatherAPI


def delta_link(request):
    latitude = request.session['location']['latitude']
    longitude = request.session['location']['longitude']

    area = request.session['solar_panel']['area']
    efficiency = request.session['solar_panel']['efficiency']
    pr = request.session['solar_panel']['pr']
    capacity = request.session['solar_panel']['capacity']

    solar_panel = SolarPanel(efficiency, area, pr, capacity)

    ow_api = OpenWeatherAPI()

    ow_api.download(latitude, longitude)
    ow_df = ow_api.get_dataframe()

    delta_model = Delta(solar_panel)
    delta_model.predict(ow_df, latitude, longitude)

    results = dict(
        hour=delta_model.hour(),
        day=delta_model.day(),
        five_days=delta_model.five_days(),
        month=delta_model.month(),
        year=delta_model.year()
    )

    for key, val in results.items():
        results[key] = round(val, 2)

    return results

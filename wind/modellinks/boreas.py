from windpower.Boreas import Boreas
from windpower.WindTurbine import WindTurbine


def boreas_link(request):
    latitude = request.session['location']['latitude']
    longitude = request.session['location']['longitude']

    efficiency = request.session['wind_turbine']['efficiency']
    radius = request.session['wind_turbine']['radius']
    height = request.session['wind_turbine']['height']

    efficiency = float(efficiency)
    radius = float(radius)
    height = float(height)

    wind_turbine = WindTurbine(eff=efficiency, radius=radius, height=height)

    boreas_model = Boreas(lat=latitude, lon=longitude, wt=wind_turbine)

    results = dict(
        hour=boreas_model.hour(),
        day=boreas_model.day(),
        five_days=boreas_model.five_days(),
        month=boreas_model.month(),
        year=boreas_model.year()
    )

    for key, val in results.items():
        results[key] = round(val, 2)

    return results
from windpower.WindTurbine import WindTurbine
from windpower.Aeolus import Aeolus


def aeolus_link(request):
    latitude = request.session['location']['latitude']
    longitude = request.session['location']['longitude']

    efficiency = request.session['wind_turbine']['efficiency']
    radius = request.session['wind_turbine']['radius']
    height = request.session['wind_turbine']['height']

    efficiency = float(efficiency)
    radius = float(radius)
    height = float(height)

    wind_turbine = WindTurbine(eff=efficiency, radius=radius, height=height)

    aeolus_model = Aeolus(lat=latitude, lon=longitude, turbine=wind_turbine)


    results = dict(
        hour=aeolus_model.hour(),
        day=aeolus_model.day(),
        five_days=aeolus_model.five_days(),
        month=aeolus_model.month(),
        year=aeolus_model.year()
    )

    for key, val in results.items():
        results[key] = round(val, 2)

    return results


from SolarIrrad.models.alpha import Alpha
from SolarIrrad.models.model import SolarPanel


def alpha_link(request):
    latitude = request.session['location']['latitude']
    longitude = request.session['location']['longitude']

    area = request.session['solar_panel']['area']
    efficiency = request.session['solar_panel']['efficiency']
    pr = request.session['solar_panel']['pr']
    capacity = request.session['solar_panel']['capacity']

    solar_panel = SolarPanel(efficiency, area, pr, capacity)

    alpha_model = Alpha(latitude, longitude, solar_panel)

    results = dict(
        hour=alpha_model.hour(),
        day=alpha_model.day(),
        five_days=alpha_model.five_days(),
        month=alpha_model.month(),
        year=alpha_model.year()
    )

    for key, val in results.items():
        results[key] = round(val, 2)

    return results

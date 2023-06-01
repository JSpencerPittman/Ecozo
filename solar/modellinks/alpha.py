from SolarIrrad.models.alpha import WCAlpha
from SolarIrrad.models.model import SolarPanel


def alpha_link(request):
    latitude = request.session['location']['latitude']
    longitude = request.session['location']['longitude']

    area = request.session['solar_panel']['area']
    efficiency = request.session['solar_panel']['efficiency']
    pr = request.session['solar_panel']['pr']
    capacity = request.session['solar_panel']['capacity']

    solar_panel = SolarPanel(efficiency, area, pr, capacity)

    wc_alpha_model = WCAlpha(latitude, longitude, solar_panel)

    results = dict(
        hour=wc_alpha_model.hour(),
        day=wc_alpha_model.day(),
        five_days=wc_alpha_model.five_days(),
        month=wc_alpha_model.month(),
        year=wc_alpha_model.year()
    )

    for key, val in results.items():
        results[key] = round(val, 2)

    return results

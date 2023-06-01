from SolarIrrad.models.charlie import Charlie
from SolarIrrad.models.model import SolarPanel


def charlie_link(request):
    latitude = request.session['location']['latitude']
    longitude = request.session['location']['longitude']

    area = request.session['solar_panel']['area']
    efficiency = request.session['solar_panel']['efficiency']
    pr = request.session['solar_panel']['pr']
    capacity = request.session['solar_panel']['capacity']

    solar_panel = SolarPanel(efficiency, area, pr, capacity)

    charlie_model = Charlie(latitude, longitude, solar_panel)

    results = dict(
        hour=charlie_model.hour(),
        day=charlie_model.day(),
        five_days=charlie_model.five_days(),
        month=charlie_model.month(),
        year=charlie_model.year()
    )

    for key, val in results.items():
        results[key] = round(val, 2)

    return results

from SolarIrrad.WC_ALPHA import WCAlpha
from PowerGeneration.PowerCalc import SolarPanel


def wc_alpha_link(request):
    latitude = request.session['location']['latitude']
    longitude = request.session['location']['longitude']

    wc_alpha_model = WCAlpha(latitude, longitude)

    results = dict(
        hour=wc_alpha_model.hour(),
        day=wc_alpha_model.day(),
        five_days=wc_alpha_model.five_days(),
        month=wc_alpha_model.month(),
        year=wc_alpha_model.year()
    )

    print("INTERMEDIARY RESULTS")
    print(results)

    area = request.session['solar_panel']['area']
    efficiency = request.session['solar_panel']['efficiency']
    pr = request.session['solar_panel']['pr']

    sol_pan = SolarPanel(efficiency, area, pr)

    for key, val in results.items():
        new_val = sol_pan.calc_generated_power(val)
        results[key] = round(new_val, 2)

    print("WC ALPHA MODEL RAN")

    return results

from django.urls import path
from solar.views import solar, solar_geo, solar_panel
from wind.views import wind, wind_geo, wind_turbine
from insights.views import insights
from home.views import home
from contact.views import contact

urlpatterns = [
    path('solar/', solar, name='Solar'),
    path('solar/geo', solar_geo, name='SolarGeo'),
    path('solar/solar-panel', solar_panel, name="SolarPanel"),

    path('wind/', wind, name='Wind'),
    path('wind/geo', wind_geo, name='WindGeo'),
    path('wind/wind-turbine', wind_turbine, name='WindTurbine'),

    path('insights/', insights, name='Insights'),
    path('', home, name='Home'),
    path('contact/', contact, name='Contact')
]

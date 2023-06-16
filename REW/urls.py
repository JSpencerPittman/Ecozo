"""
URL configuration for REW project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
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

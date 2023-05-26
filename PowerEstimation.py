class GeoLocation(object):
    def __init__(self, lat: float, lon: float):
        self.longitude = float(lon)
        self.latitude = float(lat)

    def coordinates(self):
        return self.longitude, self.latitude


class SolarPanel(object):
    def __init__(self, cap: float, eff: float, area: float):
        self.capacity = float(cap)
        self.efficiency = float(eff)
        self.area = float(area)


class SolarExposure(object):
    def __init__(self, irr: float, dur: float):
        self.intensity = float(irr)
        self.duration = float(dur)

        
class PowerEstimation(object):
    def __init__(self, loc: GeoLocation, panel: SolarPanel, exposure: SolarExposure):
        self.loc = loc
        self.panel = panel
        self.exposure = exposure

    def power_generated(self):
        pan_pow = self.panel.efficiency * self.panel.capacity * self.panel.area
        exp_pow = self.exposure.intensity * self.exposure.duration
        return pan_pow * exp_pow


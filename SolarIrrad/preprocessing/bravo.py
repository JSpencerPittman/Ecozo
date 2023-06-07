from abc import abstractmethod
from SolarIrrad.preprocessing.DataPreprocessor import DataPreprocessor
import math
from datetime import datetime
import ephem
import pytz

WINTER_SOLSTICE_DOY = 355
MIDNIGHT = 0
CLOUDINESS_AVG = 30
RAD2DEG = 180 / math.pi


class DataPreprocessorBravo(DataPreprocessor):
    def __init__(self, data):
        super().__init__(data)

    @abstractmethod
    def format(self):
        pass

    def _add_wint_sol(self):
        def calc_dist_from_wint_sol(doy):
            return min(abs(doy - WINTER_SOLSTICE_DOY), abs(doy + (365 - WINTER_SOLSTICE_DOY)))

        self.data['wint_sol'] = self.data.day_of_year.map(calc_dist_from_wint_sol)

    def _add_midnight(self):
        def calc_dist_from_midnight(di):
            return min(abs(di - MIDNIGHT), abs((MIDNIGHT + 48) - di))

        self.data['midnight'] = self.data.daily_index.map(calc_dist_from_midnight)

    @abstractmethod
    def _add_blockage(self):
        pass

    @abstractmethod
    def _trim_columns(self):
        pass


class DataPreprocessorPSM3(DataPreprocessorBravo):
    def __init__(self, data):
        super().__init__(data)

    def format(self):
        super()._add_wint_sol()
        super()._add_midnight()
        self._add_blockage()
        self._add_cloudiness()
        self._trim_columns()

        return self.data

    def _add_blockage(self):
        cloud_intensity_mapping = {
            'Clear': 0,
            'Probably Clear': 0,
            'Cirrus': 0,
            'Overshooting': 0,
            'Super-Cooled Water': 1,
            'Overlapping': 1,
            'Fog': 2,
            'Opaque Ice': 2,
            'Water': 2,
            'Unknown': 2
        }
        self.data['blockage'] = self.data['Cloud Type'].map(cloud_intensity_mapping)

    def _add_cloudiness(self):
        def calc_cloudiness(row):
            if row['Clearsky DNI'] != 0:
                dni_rat = row['DNI'] / row['Clearsky DNI']
                return (1 - dni_rat) * 100
            else:
                return CLOUDINESS_AVG

        self.data['cloudiness'] = self.data.apply(calc_cloudiness, axis=1)

    def _trim_columns(self):
        # Time measurements that were replaced with more helpful metrics
        unnecessary_columns = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'day_of_year', 'daily_index']
        # System variables
        unnecessary_columns += ['index', 'Fill Flag']
        # Data were trying to predict
        unnecessary_columns += ['Global Horizontal UV Irradiance (280-400nm)',
                                'Global Horizontal UV Irradiance (295-385nm)',
                                'DHI', 'GHI', 'Clearsky DHI', 'Clearsky GHI', 'Clearsky DNI']
        # No available data in OpenWeatherAPI
        unnecessary_columns += ['Dew Point', 'Surface Albedo', 'Precipitable Water', 'Cloud Type']
        self.data.drop(unnecessary_columns, axis=1, inplace=True)


class DataPreprocessorOpenWeather(DataPreprocessorBravo):
    def __init__(self, data, lat, lon):
        super().__init__(data)
        self.lat = lat
        self.lon = lon

    def format(self):
        # Add PSM3 specific features
        self._add_doy()
        self._add_daily_index()
        self._add_sza()

        # Add new features specific to model
        super()._add_wint_sol()
        super()._add_midnight()
        self._add_blockage()
        self._trim_columns()

        # Match the names and column ordering of the psm3 data
        self._arrange_columns()

        return self.data

    def _add_doy(self):
        def calc_doy(dt):
            return datetime.fromtimestamp(dt).timetuple().tm_yday

        self.data['day_of_year'] = self.data.datetime.map(calc_doy)

    def _add_daily_index(self):
        def calc_daily_index(dt):
            return datetime.fromtimestamp(dt).hour * 2

        self.data['daily_index'] = self.data.datetime.map(calc_daily_index)

    def _add_sza(self):
        def calc_sza(dt):
            # Convert to UTC
            dt = datetime.fromtimestamp(dt)
            utc_dt = dt.astimezone(pytz.utc)

            # Establish Observer
            obs = ephem.Observer()
            obs.lat = str(self.lat)
            obs.lon = str(self.lon)
            obs.date = utc_dt

            # Establish Sun
            sun = ephem.Sun()
            sun.compute(obs)

            angle_above_horizon = float(sun.alt) * RAD2DEG
            return 90 - angle_above_horizon

        self.data['Solar Zenith Angle'] = self.data.datetime.map(calc_sza)

    def _add_blockage(self):
        def map_weather_to_blockage(weather_id):
            weather_id = str(weather_id)

            # 8XX - Clear or Clouds
            if weather_id[0] == '8':
                # 800 and 801 - Clear or mostly Clear
                if weather_id[2] in ['0', '1']:
                    return 0
                # 802 and 803 - half-and-half
                elif weather_id[2] in ['2', '3']:
                    return 1
                # 804 - Cloudy
                else:
                    return 2
            # 3XX - Drizzle
            elif weather_id[0] == '3':
                return 1
            else:
                return 2

        self.data['blockage'] = self.data['weather_id'].map(map_weather_to_blockage)

    def _trim_columns(self):
        unnecessary_columns = ['feels_like', 'temp_min', 'temp_max', 'sea_level',
                               'grnd_level', 'gust', 'description', 'weather', 'weather_id', 'datetime', 'hour', 'day',
                               'day_of_year', 'daily_index']
        self.data.drop(unnecessary_columns, axis=1, inplace=True)

    def _arrange_columns(self):
        # Match Column Names
        column_names = {
            'temp': 'Temperature',
            'pressure': 'Pressure',
            'humidity': 'Relative Humidity',
            'speed': 'WindPower Speed',
            'deg': 'WindPower Direction',
        }
        self.data.rename(columns=column_names, inplace=True)

        # Match Column Ordering
        ordering = ['Temperature', 'Relative Humidity', 'Solar Zenith Angle', 'Pressure',
                    'WindPower Direction', 'WindPower Speed', 'wint_sol', 'midnight',
                    'blockage', 'cloudiness']
        self.data = self.data[ordering]

import pandas as pd


class AltitudeRange(object):
    def __init__(self, low, high):
        self.low_alt = low
        self.high_alt = high

    def diff(self):
        return self.high_alt - self.low_alt


class AtmosphericData(object):
    def __init__(self):
        self.data = None
        self.data_add_cnt = 0

        self.altitudes = [0, 10, 40, 60, 80, 100, 120, 140, 160, 200]
        self.pres_altitudes = [0, 100, 200]

    def add_windtk_data(self, new_data: pd.DataFrame):
        new_data = self._format_windtk_data(new_data)

        if self.data is None:
            self.data = new_data
            self.data_add_cnt += 1
        else:
            self.data = self._merge_data(new_data)
            self.data_add_cnt += 1

    def get_alt_range(self, alt: int) -> AltitudeRange:
        i = 1
        while i < len(self.altitudes) and alt > self.altitudes[i]:
            i += 1
        lower, higher = self.altitudes[i-1], self.altitudes[i]
        return AltitudeRange(lower, higher)

    def estimate_temp(self, alt: int, doy: int):
        return self._estimate(alt, doy, 'air_temp')

    def estimate_wind_speed(self, alt: int, doy: int):
        return self._estimate(alt, doy, 'wind_speed')

    def estimate_wind_dir(self, alt: int, doy: int):
        return self._estimate(alt, doy, 'wind_dir')

    def _estimate(self, alt: int, doy: int, col: str):
        alt_rng = self.get_alt_range(alt)

        low_val = self._get_specific(alt_rng.low_alt, doy, col)
        high_val = self._get_specific(alt_rng.high_alt, doy, col)

        slope = (high_val - low_val) / alt_rng.diff()
        y_intercept = low_val - slope * alt_rng.low_alt

        est_val = slope * alt + y_intercept

        return est_val

    def _get_specific_temp(self, alt: int, doy: int):
        return self._get_specific(alt, doy, 'air_temp')

    def _get_specific_wind_speed(self, alt: int, doy: int):
        return self._get_specific(alt, doy, 'wind_speed')

    def _get_specific_wind_dir(self, alt: int, doy: int):
        return self._get_specific(alt, doy, 'wind_dir')

    def _get_specific(self, alt: int, doy: int, col: str):
        if alt not in self.altitudes:
            raise Exception('No such altitude please use estimate instead!')
        group = self._doy2group(doy)
        col_name = f'{col}_{alt}m'
        return self.data.loc[group, col_name]

    def get_specific_air_pressure(self, alt: int, doy: int):
        if alt not in self.pres_altitudes:
            raise Exception('No such altitude please use estimate instead!')
        group = self._doy2group(doy)
        col_name = f'air_pressure_{alt}m'
        return self.data.loc[group, col_name]

    def _merge_data(self, new_data: pd.DataFrame):
        data_merge = []
        for i in range(self.data_add_cnt):
            data_merge.append(self.data)
        data_merge.append(new_data)
        data_merge = pd.concat(data_merge)
        data_merge.drop('index', axis=1, inplace=True)
        data_merge.groupby('group').mean()
        return data_merge

    def _format_windtk_data(self, new_data: pd.DataFrame):
        # Group the data into groups of five days
        groups = []
        for i, row in new_data.iterrows():
            groups.append(self._doy2group(row['day_of_year']))
        new_data['group'] = groups

        new_data = new_data.groupby('group').mean()

        # Drop the unnecessary columns
        unnecessary_cols = ['index', 'Year', 'Month', 'Day', 'Hour', 'Minute',
                            'day_of_year', 'daily_index', 'surface_precipitation_rate']
        new_data.drop(unnecessary_cols, axis=1, inplace=True)

        # rename surface column
        new_data.rename(columns={'surface_air_pressure': 'air_pressure_0m'}, inplace=True)

        # This column will rarely be used but will be added as a safeguard for heights below 10m
        new_data['air_temp_0m'] = new_data.air_temp_10m
        new_data['wind_speed_0m'] = new_data.wind_speed_10m
        new_data['wind_dir_0m'] = new_data.wind_dir_10m

        return new_data

    @staticmethod
    def _doy2group(doy: int):
        return (doy - 1) // 5 + 1


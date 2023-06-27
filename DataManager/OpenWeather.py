import os
import yaml
import requests
import json
import pandas as pd
from datetime import datetime
from DataManager.APIException import APIException

class OpenWeatherAPI:
    def __init__(self):
        self.par_dir = os.path.dirname(__file__)
        self.data_path = os.path.join(self.par_dir, '../data')
        self.base_url = "http://api.openweathermap.org/data/2.5/forecast"

        path = os.path.join(self.data_path, 'weather.json')
        self.downloaded = os.path.exists(path)

        # Get the API Key
        keys_path = os.path.join(self.par_dir, 'keys.yaml')
        with open(keys_path, 'r') as keys_yaml:
            keys = yaml.safe_load(keys_yaml)
        self.api_key = keys["OPEN_WEATHER_API_KEY"]

        self.latitude, self.longitude = None, None
        self.dt, self.tz = None, None

    def download(self, lat, lon):
        if self.downloaded:
            if self.latitude == lat and self.longitude == lon:
                if self.dt is not None and self.dt - (datetime.now().timestamp() + self.tz) > 0:
                    return

        self.latitude = lat
        self.longitude = lon

        parameters = [
            f"lat={lat}",
            f"lon={lon}",
            f"appid={self.api_key}"
        ]

        # Construct the URL to collect the data from
        url = f"{self.base_url}?{'&'.join(parameters)}"

        # Save the data as a JSON file
        try:
            response = requests.get(url)
            response.raise_for_status()

            weather_path = os.path.join(self.data_path, 'weather.json')
            with open(weather_path, 'w') as weather_json:
                json.dump(response.json(), weather_json)

            self.downloaded = True

            df = self.get_dataframe()
            self.dt = df.datetime.iloc[0]

            print("Weather JSON Data sucessfully downloaded.")
        except requests.exceptions.RequestException as e:
            print(f"Error occurred during the GET request: ", e)
        except IOError as e:
            print("Error occurred during the write to the file: ", e)

    def get_dataframe(self):
        if not self.downloaded:
            raise APIException("OpenWeatherAPI is not downloaded!")

        # Load the JSON file
        weather_path = os.path.join(self.data_path, 'weather.json')
        with open(weather_path, 'r') as weather_json:
            weather = json.load(weather_json)

        # Reformat the data into as a list of dictionaries
        weather_entries = []
        for entry in weather['list']:
            formatted_entry = self._format_weather_entry(entry)
            weather_entries.append(formatted_entry)

        # Convert into a pandas DataFrame
        weather_df = pd.DataFrame(weather_entries)
        self._format_weather_dataframe(weather_df)

        # Apply the timezone to datetime
        tz = int(weather['city']['timezone'])
        weather_df['datetime'] = weather_df['datetime'] + tz

        self.tz = tz

        return weather_df

    @staticmethod
    def _format_weather_entry(entry):
        def format_weather_description(desc):
            try:
                desc['weather'] = desc['main']
                desc['weather_id'] = desc['id']

                desc.pop('id')
                desc.pop('icon')
                desc.pop('main')
            except KeyError:
                pass

            return desc

        sub_data = [entry['main'], entry['clouds'], entry['wind']]

        w = format_weather_description(entry['weather'][0])
        sub_data.append(w)

        result = {}
        for d in sub_data:
            for k, v in d.items():
                result[k] = v

        result['datetime'] = entry['dt']

        return result

    @staticmethod
    def _format_weather_dataframe(df):
        def kelvin_to_fahrenheit(k):
            return (k - 273.15) * (9 / 5) + 32

        temp_cols = ['temp', 'feels_like', 'temp_min', 'temp_max']

        for col in temp_cols:
            df[col] = df[col].map(kelvin_to_fahrenheit)

        df.reset_index(inplace=True)
        df['hour'] = df.index.map(lambda i: 3 * (i % 8))
        df['day'] = df.index.map(lambda i: i // 8)

        df.rename(columns={'all': 'cloudiness'}, inplace=True)

        df.drop(['index', 'temp_kf'], axis=1, inplace=True)


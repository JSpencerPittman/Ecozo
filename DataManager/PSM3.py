import os

import psycopg2
import yaml
import requests
import numpy as np
import pandas as pd
import json
from sqlalchemy import create_engine, text
from datetime import datetime
from DataManager.APIException import APIException


class PSM3API:
    def __init__(self):
        self.par_dir = os.path.dirname(__file__)
        self.data_path = os.path.join(self.par_dir, '../data')
        self.base_url = "https://developer.nrel.gov/api/nsrdb/v2/solar/psm3-download.csv"

        path = os.path.join(self.data_path, 'psm3_data.csv')
        self.downloaded = os.path.exists(path)

        # Get the API key & Email
        keys_path = os.path.join(self.par_dir, 'keys.yaml')
        with open(keys_path, 'r') as keys_yaml:
            keys = yaml.safe_load(keys_yaml)
        self.api_key = keys["NREL_API_KEY"]
        self.email = keys["EMAIL"]

        self.latitude, self.longitude, self.year = None, None, None

        self.postgres_url = keys["POSTGRES_URL"]
        self.tabelized = self._table_exists()

    def establish_connnection(self, engine=False):
        if engine:
            engine = create_engine(self.postgres_url)
            try:
                cnx = engine.connect()
                return cnx
            except Exception as e:
                print("Failed to connect to Ecozo database: ", e)
        else:
            try:
                cnx = psycopg2.connect(self.postgres_url)
                return cnx
            except Exception as e:
                print("Failed to connect to Ecozo database: ", e)

    def download(self, lat, lon, year):
        self.latitude, self.longitude = lat, lon
        self.year = year

        parameters = [
            f"wkt=POINT({self.longitude}%20{self.latitude})",
            f"names={self.year}",
            f"interval=30",
            f"utc=false",
            f"email={self.email}",
            f"api_key={self.api_key}"
        ]

        # Construct the URL to collect the data from
        url = f"{self.base_url}?{'&'.join(parameters)}"

        # Save the data as a CSV file
        try:
            response = requests.get(url)
            response.raise_for_status()

            psm3_path = os.path.join(self.data_path, 'psm3_data.csv')
            with open(psm3_path, 'wb') as psm3_csv:
                psm3_csv.write(response.content)

            self.downloaded = True

            print("PSM3 Data saved as CSV successfully.")
        except requests.exceptions.RequestException as e:
            print("Error ocurred during the GET request: ", e)
        except IOError as e:
            print("Error occurred during the write to the file: ", e)

    def tabelize(self):
        if not self.downloaded:
            raise APIException("PSM3 is not downloaded!")

        psm3_path = os.path.join(self.data_path, 'psm3_data.csv')
        psm3_data = pd.read_csv(psm3_path, low_memory=False)

        # Handle Header Data
        meta_data = dict(zip(psm3_data.columns, list(psm3_data.iloc[0])))
        columns = list(psm3_data.iloc[1])
        psm3_data.drop(index=[0, 1], inplace=True)
        psm3_data.columns = columns
        psm3_data = psm3_data[[col for col in columns if type(col) == str]]

        psm3_data.reset_index(inplace=True, drop=True)

        #  Make a way to index days without relying on months
        days_of_year = pd.DataFrame(np.repeat(np.arange(1, 366), 48))
        psm3_data = pd.concat([psm3_data, days_of_year], axis=1)
        psm3_data.rename(columns={0: 'day_of_year'}, inplace=True)

        # Save the data in postgresql
        cnx = self.establish_connnection(engine=True)

        # Drop the table if it already exists
        if self._table_exists():
            drop_query = text('DROP TABLE psm3;')
            cnx.execute(drop_query)
            cnx.commit()

        psm3_data.to_sql(name='psm3', con=cnx)
        cnx.commit()

        cnx.close()

        # Save the metadata to a JSON file
        meta_json = json.dumps(meta_data, indent=4)
        meta_path = os.path.join(self.data_path, 'weather_meta.json')
        with open(meta_path, 'w') as meta_file:
            meta_file.write(meta_json)

        self.tabelized = True

    def get_dataframe(self, m=None, d=None, t1=None, t2=None):
        if not self.tabelized:
            raise APIException("PSM3 is not tabelized!")

        res_df = None

        # Single day
        if m is not None and d is not None:
            doy = self._date_to_doy(m, d)
            res_df = self._get_dataframe_for_day(doy)
        elif t1 is not None and t2 is None:
            doy = self._date_to_doy(*t1)
            res_df = self._get_dataframe_for_day(doy)
        # Multiple days
        elif t1 is not None and t2 is not None:
            doy1 = self._date_to_doy(*t1)
            doy2 = self._date_to_doy(*t2)
            res_df = self._get_dataframe_for_range(doy1, doy2)
        # Bad Input
        else:
            raise APIException("Not enough data provided to PSM3!")

        self._format_psm3_dataframe(res_df)
        return res_df

    def _table_exists(self):
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"

        cnx = self.establish_connnection()
        cur = cnx.cursor()

        cur.execute(query)
        tables = cur.fetchall()
        tables = [t[0] for t in tables]

        cur.close()
        cnx.close()

        return 'psm3' in tables

    def _get_dataframe_for_range(self, doy1, doy2):
        search_query = f"SELECT * FROM psm3 WHERE day_of_year >= {doy1} AND day_of_year <= {doy2}"
        search_query = text(search_query)

        cnx = self.establish_connnection(engine=True)

        df = pd.read_sql(search_query, con=cnx)

        cnx.close()

        return df

    def _get_dataframe_for_day(self, doy):
        search_query = f"SELECT * FROM psm3 WHERE day_of_year = {doy}"

        cnx = self.establish_connnection(engine=True)

        df = pd.read_sql(search_query, con=cnx)

        cnx.close()

        return df

    @staticmethod
    def _date_to_doy(month, day):
        date = datetime(2001, month, day)
        doy = date.timetuple().tm_yday
        return doy

    def _format_psm3_dataframe(self, df):
        # Convert Temperatures
        def cel2fah(c):
            return (int(c) * (9 / 5)) + 32

        df['Temperature'] = df['Temperature'].map(cel2fah)
        df['Dew Point'] = df['Dew Point'].map(cel2fah)

        # Map Meta Data to cloud types
        meta_path = os.path.join(self.data_path, 'weather_meta.json')
        with open(meta_path, 'r') as meta_json:
            meta_data = json.load(meta_json)
        cloud_mapping = {}
        for key, value in meta_data.items():
            if key.startswith('Cloud Type'):
                cloud_mapping[key.split(' ')[-1]] = value
        df['Cloud Type'] = df['Cloud Type'].map(cloud_mapping)

        # Map Data Types
        int_cols = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Clearsky DHI',
                    'Clearsky DNI', 'Clearsky GHI', 'Dew Point', 'Pressure',
                    'DHI', 'DNI', 'GHI']
        float_cols = ['Solar Zenith Angle', 'Relative Humidity', 'Precipitable Water', 'Surface Albedo',
                      'Wind Direction', 'Wind Speed', 'Global Horizontal UV Irradiance (280-400nm)',
                      'Global Horizontal UV Irradiance (295-385nm)']

        for col in int_cols:
            df[col] = df[col].astype(int)

        for col in float_cols:
            df[col] = df[col].astype(float)

        # Index the entries based on time of day
        def daily_index(row):
            return row.Hour * 2 + (row.Minute / 30)
        df['daily_index'] = df.apply(daily_index, axis=1)

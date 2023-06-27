import os
import yaml
import requests
import sqlite3
import numpy as np
import pandas as pd
from sqlalchemy import text, create_engine
import psycopg2
from datetime import datetime
from DataManager.APIException import APIException


class WindTKAPI:
    def __init__(self):
        self.par_dir = os.path.dirname(__file__)
        self.data_path = os.path.join(self.par_dir, '../data')
        self.base_url = "https://developer.nrel.gov/api/wind-toolkit/v2/wind/wtk-download.csv"

        path = os.path.join(self.data_path, 'windtk_data.csv')
        self.downloaded = os.path.exists(path)

        # Get the API key & Email
        keys_path = os.path.join(self.par_dir, 'keys.yaml')
        with open(keys_path, 'r') as keys_yaml:
            keys = yaml.safe_load(keys_yaml)
        self.api_key = keys["NREL_API_KEY"]
        self.email = keys["EMAIL"]

        self.latitude = None
        self.longitude = None
        self.year = None

        self.postgres_url = keys["POSTGRES_URL"]
        self.tabelized = self._table_exists()

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

            windtk_path = os.path.join(self.data_path, 'windtk_data.csv')
            with open(windtk_path, 'wb') as windtk_csv:
                windtk_csv.write(response.content)

            self.downloaded = True

            print("WindTK Data saved as CSV successfully.")
        except requests.exceptions.RequestException as e:
            print("Error ocurred during the GET request: ", e)
        except IOError as e:
            print("Error occurred during the write to the file: ", e)

    def tabelize(self):
        if not self.downloaded:
            raise APIException("WindTK is not downloaded!")

        windtk_path = os.path.join(self.data_path, 'windtk_data.csv')
        windtk_data = pd.read_csv(windtk_path, low_memory=False, skiprows=1)

        days_of_year = pd.DataFrame(np.repeat(np.arange(1, 366), 48))
        windtk_data = pd.concat([windtk_data, days_of_year], axis=1)
        windtk_data.rename(columns={0: 'day_of_year'}, inplace=True)

        dep_cols = [col for col in windtk_data.columns if ('DEPRECATED' in col)]
        windtk_data.drop(dep_cols, axis=1, inplace=True)

        # Save the data in postgresql
        cnx = self.establish_connnection(engine=True)

        # Drop the table if it already exists
        if self._table_exists():
            drop_query = text('DROP TABLE windtk;')
            cnx.execute(drop_query)
            cnx.commit()

        windtk_data.to_sql(name='windtk', con=cnx)
        cnx.commit()

        cnx.close()

        self.tabelized = True

    def get_dataframe(self, m=None, d=None, t1=None, t2=None):
        if not self.tabelized:
            raise APIException("WindTK is not tabelized!")

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
            raise APIException("Not enough data provided to WindTK!")

        self._format_windtk_dataframe(res_df)
        return res_df

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

    def _table_exists(self):
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"

        cnx = self.establish_connnection()
        cur = cnx.cursor()

        cur.execute(query)
        tables = cur.fetchall()
        tables = [t[0] for t in tables]

        cur.close()
        cnx.close()

        return 'windtk' in tables

    def _get_dataframe_for_range(self, doy1, doy2):
        search_query = f"SELECT * FROM windtk WHERE day_of_year >= {doy1} AND day_of_year <= {doy2}"
        search_query = text(search_query)

        cnx = self.establish_connnection(engine=True)

        df = pd.read_sql(search_query, con=cnx)

        cnx.close()

        return df

    def _get_dataframe_for_day(self, doy):
        search_query = f"SELECT * FROM windtk WHERE day_of_year = {doy}"

        cnx = self.establish_connnection(engine=True)

        df = pd.read_sql(search_query, con=cnx)

        cnx.close()

        return df

    def _date_to_doy(self, month, day):
        date = datetime(2001, month, day)
        doy = date.timetuple().tm_yday
        return doy

    def _format_windtk_dataframe(self, df):
        df.columns = [self._simplify_col_name(col) for col in df.columns]

        # Temperature Conversions
        def cel2fah(c):
            return (int(c) * (9 / 5)) + 32

        temp_cols = [col for col in df.columns if 'temp' in col]
        for col in temp_cols:
            df[col] = df[col].map(cel2fah)

        # Daily Index 0-48 in 30min intervals
        def daily_index(row):
            return row.Hour * 2 + (row.Minute / 30)

        df['daily_index'] = df.apply(daily_index, axis=1)

    @staticmethod
    def _simplify_col_name(col):
        if '(' in col:
            col = col.split(' (')[0]
        col = col.replace(' at ', ' ')
        col = col.replace(' ', '_')
        col = col.replace('direction', 'dir')
        col = col.replace('temperature', 'temp')
        return col

import os
import requests
import sqlite3
import numpy as np
import pandas as pd
import zipfile
import io
import rasterio
from rasterio.transform import rowcol
from affine import Affine


class PSM3API:
    def __init__(self):
        self.par_dir = os.path.dirname(__file__)
        self.data_path = os.path.join(self.par_dir, '../data/worldclim')
        self.sql_path = os.path.join(self.par_dir, '../data/data.db')
        self.base_url = "https://biogeo.ucdavis.edu/data/worldclim/v2.1/base"

        path = os.path.join(self.data_path, 'worldclim')
        self.downloaded = os.path.exists(path)

        self.tabelized = self._table_exists()

        self.globe_height = 1080
        self.globe_width = 2160
        self.globe_rows = np.repeat(np.arange(self.globe_height), self.globe_width).reshape(-1,1)
        self.globe_cols = np.array(list(range(self.globe_width)) * self.globe_height).reshape(-1,1)

        self.datasets = {
            "tmin": "wc2.1_10m_tmin.zip",
            "tmax": "wc2.1_10m_tmax.zip",
            "tavg": "wc2.1_10m_tavg.zip",
            "prec": "wc2.1_10m_prec.zip",
            "srad": "wc2.1_10m_srad.zip",
            "wind": "wc2.1_10m_wind.zip",
            "vapr": "wc2.1_10m_vapr.zip",
            "elev": "wc2.1_10m_elev.zip"
        }

    def download(self):
        for i, (name, file_name) in enumerate(self.datasets.items()):
            url = f"{self.base_url}/{file_name}"

            try:
                print(f"Downloading {name} data {i+1}/{len(self.datasets)}...")

                response = requests.get(url, stream=True)
                response.raise_for_status()

                file_path = os.path.join(self.data_path, name)
                z = zipfile.ZipFile(io.BytesIO(response.content))
                z.extractall(file_path)

                # Rename files
                if name != 'elev':
                    for j in range(1, 13):
                        file_name = f"wc2.1_10m_{name}_{'0'+str(j) if j < 10 else j}.tif"
                        new_file_name = f"{name}_{j}.tif"
                        os.rename(os.path.join(file_path, file_name), os.path.join(file_path, new_file_name))
                else:
                    os.rename(os.path.join(file_path, 'wc2.1_10m_elev.tif'), os.path.join(file_path, 'elev.tif'))

                print(f"{name} zip file successfully extracted.")
            except requests.exceptions.RequestException as e:
                print(f"Error occurred during the GET request for {name}: ", e)

    def tabelize(self):
        if not self.downloaded:
            raise APIException("WorldClim is not downloaded!")

        wc_df = np.hstack([self.globe_rows, self.globe_cols])
        wc_df = pd.DataFrame(wc_df, columns=['row', 'col'])
        cnt = 1

        con = sqlite3.connect(self.sql_path)
        cur = con.cursor()

        # Drop the table if it already exists
        try:
            cur.execute('DROP TABLE WorldClim;')
        except sqlite3.OperationalError:
            pass

        wc_df.to_sql(name="WorldClim", con=con)

        for directory, _, files in os.walk(self.data_path):
            for file in files:
                if file.split('.')[1] != 'tif':
                    continue

                file_path = os.path.join(directory, file)
                name = file.split('.')[0]

                print(cnt, name)
                cnt += 1

                df = self._geotif_to_dataframe(file_path)
                df.rename(columns={'data': name}, inplace=True)

                df.to_sql(name=name, con=con)

                new_col_command = f"ALTER TABLE WorldClim ADD COLUMN {name} INT;"
                cur.execute(new_col_command)

                fill_col_command = f"UPDATE WorldClim SET {name} = {name}.{name} FROM {name} WHERE WorldClim.'index' = {name}.'index';"
                cur.execute(fill_col_command)

                drop_table_command = f"DROP TABLE {name};"
                cur.execute(drop_table_command)

                con.commit()

        cur.close()
        con.close()

        self.tabelized = True

    def get_dataframe(self, lat, lon, regional=False):
        if not self.tabelized:
            raise APIException("WorldClim is not tabelized!")

        loc_row, loc_col = self._coordinates_to_index(lat, lon)

        con = sqlite3.connect(self.sql_path)
        cur = con.cursor()

        search_query = f"SELECT * FROM WorldClim"

        if regional:
            cond1 = f"row >= {loc_row - 2} AND row <= {loc_row + 2}"
            cond2 = f"col >= {loc_col - 2} AND col <= {loc_col + 2}"
            search_query = f"{search_query} WHERE {cond1} AND {cond2};"
        else:
            search_query = f"{search_query} WHERE row={loc_row} AND col={loc_col}"

        df = pd.read_sql(search_query, con)

        cur.close()
        con.close()

        return df


    @staticmethod
    def _table_exists():
        query = "SELECT Count(name) FROM sqlite_master WHERE type='table' AND name='psm3'"

        con = sqlite3.connect("my_data.db")
        cur = con.cursor()
        response = pd.read_sql(query, con)
        cur.close()
        con.close()

        return bool(response.iloc[0,0])

    def _geotif_to_dataframe(self, tif_path):
        dataset = rasterio.open(tif_path)
        data = dataset.read(1).ravel().reshape(-1, 1)

        res = np.hstack([self.globe_rows, self.globe_cols, data])
        return pd.DataFrame(res, columns=['row', 'col', 'data'])

    @staticmethod
    def _coordinates_to_index(lat, lon):
        transform = Affine(1 / 6, 0, -180, 0, -1 / 6, 90)
        return rowcol(transform, lon, lat)

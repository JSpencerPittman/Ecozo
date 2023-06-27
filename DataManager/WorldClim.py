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


MONTHS_IN_YEAR = 12

class WorldClimAPI:
    def __init__(self):
        self.par_dir = os.path.dirname(__file__)
        self.data_path = os.path.join(self.par_dir, '../data/worldclim')
        self.base_url = "https://biogeo.ucdavis.edu/data/worldclim/v2.1/base"

        self.downloaded = os.path.exists(self.data_path)

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

        self.downloaded = True

    def get_dataframe(self, lat, lon):
        loc_row, loc_col = self._coordinates_to_index(lat, lon)

        vals = {}

        for directory, _, files in os.walk(self.data_path):
            if len(files) > 0:
                feat_name = directory.split('/')[-1]
                vals[feat_name] = [0] * MONTHS_IN_YEAR

            for file in files:
                if file.split('.')[1] != 'tif':
                    continue

                file_path = os.path.join(directory, file)

                val = self._get_geotiff_data_at_location(file_path, loc_row, loc_col)

                feat = file.split('.')[0].split('_')

                if feat[0] == 'elev':
                    vals['elev'] = [val] * MONTHS_IN_YEAR
                else:
                    feat, month = feat[0], int(feat[1])
                    vals[feat][month-1] = val

        df = pd.DataFrame(vals)

        def cel2fah(c):
            return (c * 9 / 5) + 32
        temp_cols = [col for col in df.columns if col.startswith('t')]
        for col in temp_cols:
            df[col] = df[col].map(cel2fah)

        return df

    @staticmethod
    def _get_geotiff_data_at_location(tif_path, row, col):
        geotif = rasterio.open(tif_path).read(1)
        return geotif[row, col]

    @staticmethod
    def _coordinates_to_index(lat, lon):
        transform = Affine(1 / 6, 0, -180, 0, -1 / 6, 90)
        return rowcol(transform, lon, lat)

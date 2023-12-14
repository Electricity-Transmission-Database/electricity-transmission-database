"""Helper module to create subregions 

This module must be run from the "src/" directory

This module should only be run if shapefiles need to be recreated. All data is originally 
taken from GADM at https://gadm.org/index.html
"""

import geopandas as gpd
import pandas as pd
from typing import Dict
import requests
from pathlib import Path 
import zipfile
import shutil

AUS_MAPPER = {
    "AustralianCapitalTerritory":"SW",
    "NewSouthWales":"SW",
    "NorthernTerritory":"NT",
    "Queensland":"QL",
    "SouthAustralia":"SA",
    "Tasmania":"TA",
    "Victoria":"VI",
    "WesternAustralia":"WA",
}

def make_shapefile(geojson: str, country: str, mapper: Dict[str,str], save: str = "./") -> None:
    """Makes subregions data at a country level and saves as a shapefile
        
    Arguments: 
        geojson: str
            Admin level 1 geojson taken from GADM at https://gadm.org/index.html
        country: str
            3-letter iso code for country
            
    Returns: 
        Saves data as a shapefile as "../data/shapefiles/<country>/<country>.shp
    
        Saved data has attributes:
            REGION: country 3-letter iso
            SUBREGION: regional code for transmission database 
            geometry: geometry describing region 
    """
    
    gdf = gpd.read_file(geojson)
    assert (gdf.GID_0 == country).all()
    gdf = assign_subregions(gdf, mapper)
    gdf.to_file(Path(save,f"{country}.shp"), driver="ESRI Shapefile")
    
def assign_subregions(gdf: gpd.GeoDataFrame, mapper: Dict[str,str]) -> gpd.GeoDataFrame:
    """Assigns subregions to spatial data"""
    
    gdf = gdf[["GID_0", "NAME_1", "geometry"]].rename(columns={"GID_0":"REGION"})
    gdf["SUBREGION"] = gdf["NAME_1"].map(mapper)
    return gdf.dissolve(by="SUBREGION").reset_index()[["REGION", "SUBREGION", "geometry"]]

def download_file(url: str, destination: str):
    """downloads a file"""
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, "wb") as file:
            file.write(response.content)
        print(f"File downloaded successfully to {destination}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def unzip_file(zip_file: str, destination: str):
    """unzips a folders contents"""
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(destination)

def file_exists(file_path: str) -> bool:
    """Checks if a file exists"""
    path = Path(file_path)
    return path.is_file()

if __name__ == "__main__":
    
    data = [
        ("./../data/geojson/gadm41_AUS_1.json", "AUS", AUS_MAPPER)
    ]
    
    for geojson, country, mapper in data:
        if not file_exists(geojson):
            file_name = Path(geojson).name
            url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/json/{file_name}.zip"
            download_file(url, f"./{file_name}.zip")
            unzip_file(f"./{file_name}.zip", f"./{file_name}")
            shutil.move(f"./{file_name}/{file_name}", geojson)
            Path(file_name).rmdir()
            Path(f"{file_name}.zip").unlink()
        save_dir = Path("./","..","data","shapefiles",country)
        save_dir.mkdir(exist_ok=True)
        make_shapefile(geojson, country, mapper, save_dir)
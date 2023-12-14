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
    # "AshmoreandCartierIslands":"",
    "AustralianCapitalTerritory":"SW",
    # "CoralSeaIslandsTerritory":"",
    # "JervisBayTerritory":"",
    "NewSouthWales":"SW",
    "NorthernTerritory":"NT",
    "Queensland":"QL",
    "SouthAustralia":"SA",
    "Tasmania":"TA",
    "Victoria":"VI",
    "WesternAustralia":"WA",
}

BRA_MAPPER = {
    "Acre":"WE",
    "Alagoas":"NE",
    "Amapá":"NW",
    "Amazonas":"NW",
    "Bahia":"NE",
    "Ceará":"NE",
    "DistritoFederal":"CW",
    "EspíritoSanto":"SE",
    "Goiás":"CW",
    "Maranhão":"CN",
    "MatoGrosso":"CW",
    "MatoGrossodoSul":"CW",
    "MinasGerais":"SE",
    "Pará":"CN",
    "Paraíba":"NE",
    "Paraná":"SO",
    "Pernambuco":"NE",
    "Piauí":"NE",
    "RiodeJaneiro":"SE",
    "RioGrandedoNorte":"NE",
    "RioGrandedoSul":"SO",
    "Rondônia":"WE",
    "Roraima":"NW",
    "SantaCatarina":"SO",
    "SãoPaulo":"SE",
    "Sergipe":"NE",
    "Tocantins":"CN",
}

CAN_MAPPER = {
    "Alberta":"AB",
    "BritishColumbia":"BC",
    "Manitoba":"MB",
    "NewBrunswick":"AR",
    "NewfoundlandandLabrador":"NL",
    "NorthwestTerritories":"NO",
    "NovaScotia":"AR",
    "Nunavut":"NO",
    "Ontario":"ON",
    "PrinceEdwardIsland":"AR",
    "Québec":"QC",
    "Saskatchewan":"SK",
    "Yukon":"NO",
}

IDN_MAPPER = {
    "Aceh":"SM",
    "Bali":"NU",
    "BangkaBelitung":"SM",
    "Banten":"JW",
    "Bengkulu":"SM",
    "Gorontalo":"SL",
    "JakartaRaya":"JW",
    "Jambi":"SM",
    "JawaBarat":"JW",
    "JawaTengah":"JW",
    "JawaTimur":"JW",
    "KalimantanBarat":"KA",
    "KalimantanSelatan":"KA",
    "KalimantanTengah":"KA",
    "KalimantanTimur":"KA",
    "KalimantanUtara":"KA",
    "KepulauanRiau":"SM",
    "Lampung":"SM",
    "Maluku":"ML",
    "MalukuUtara":"ML",
    "NusaTenggaraBarat":"NU",
    "NusaTenggaraTimur":"NU",
    "Papua":"PP",
    "PapuaBarat":"PP",
    "Riau":"SM",
    "SulawesiBarat":"SL",
    "SulawesiSelatan":"SL",
    "SulawesiTengah":"SL",
    "SulawesiTenggara":"SL",
    "SulawesiUtara":"SL",
    "SumateraBarat":"SM",
    "SumateraSelatan":"SM",
    "SumateraUtara":"SM",
    "Yogyakarta":"JW"
}

IND_MAPPER = {
    "AndamanandNicobar":"",
    "AndhraPradesh":"NE",
    "ArunachalPradesh":"SO",
    "Assam":"NE",
    "Bihar":"EA",
    "Chandigarh":"NO",
    "Chhattisgarh":"EA",
    "DadraandNagarHaveli":"WE",
    "DamanandDiu":"WE",
    ########### NO DELHI (INDNO) ###########
    "Goa":"SO",
    "Gujarat":"WE",
    "Haryana":"NO",
    "HimachalPradesh":"NO",
    "JammuandKashmir":"NO",
    "Jharkhand":"EA",
    "Karnataka":"SO",
    "Kerala":"SO",
    ########### NO LADAKH (INDNO) ##########
    # "Lakshadweep":"",
    "MadhyaPradesh":"WE",
    "Maharashtra":"WE",
    "Manipur":"NE",
    "Meghalaya":"NE",
    "Mizoram":"NE",
    "Nagaland":"NE",
    # "NCTofDelhi":"",
    "Odisha":"EA",
    "Puducherry":"SO",
    "Punjab":"NO",
    "Rajasthan":"NO",
    "Sikkim":"EA",
    "TamilNadu":"SO",
    "Telangana":"SO",
    "Tripura":"NE",
    "UttarPradesh":"NO",
    "Uttarakhand":"NO",
    "WestBengal":"EA"
}

JPN_MAPPER = {
    "Aichi":"",
    "Akita":"",
    "Aomori":"",
    "Chiba":"",
    "Ehime":"",
    "Fukui":"",
    "Fukuoka":"",
    "Fukushima":"",
    "Gifu":"",
    "Gunma":"",
    "Hiroshima":"",
    "Hokkaido":"",
    "Hyōgo":"",
    "Ibaraki":"",
    "Ishikawa":"",
    "Iwate":"",
    "Kagawa":"",
    "Kagoshima":"",
    "Kanagawa":"",
    "Kochi":"",
    "Kumamoto":"",
    "Kyoto":"",
    "Mie":"",
    "Miyagi":"",
    "Miyazaki":"",
    "Nagano":"",
    "Naoasaki":"",
    "Nara":"",
    "Niigata":"",
    "Oita":"",
    "Okayama":"",
    "Okinawa":"",
    "Osaka":"",
    "Saga":"",
    "Saitama":"",
    "Shiga":"",
    "Shimane":"",
    "Shizuoka":"",
    "Tochigi":"",
    "Tokushima":"",
    "Tokyo":"",
    "Tottor":"",
}

MYS_MAPPER = {
    "Johor":"PE",
    "Kedah":"PE",
    "Kelantan":"PE",
    "KualaLumpur":"PE",
    "Labuan":"SH",
    "Melaka":"PE",
    "NegeriSembilan":"PE",
    "Pahang":"PE",
    "Perak":"PE",
    "Perlis":"PE",
    "PulauPinang":"PE",
    "Putrajaya":"PE",
    "Sabah":"SH",
    "Sarawak":"SK",
    "Selangor":"PE",
    "Trengganu":"PE",
}

PHL_MAPPER = {
    "Abra":"LU",
    "AgusandelNorte":"MI",
    "AgusandelSur":"MI",
    "Aklan":"VI",
    "Albay":"LU",
    "Antique":"VI",
    "Apayao":"LU",
    "Aurora":"LU",
    "Basilan":"MI",
    "Bataan":"LU",
    "Batanes":"LU",
    "Batangas":"LU",
    "Benguet":"LU",
    "Biliran":"VI",
    "Bohol":"VI",
    "Bukidnon":"MI",
    "Bulacan":"LU",
    "Cagayan":"LU",
    "CamarinesNorte":"LU",
    "CamarinesSur":"LU",
    "Camiguin":"MI",
    "Capiz":"VI",
    "Catanduanes":"LU",
    "Cavite":"LU",
    "Cebu":"VI",
    "CompostelaValley":"MI",
    "DavaodelNorte":"MI",
    "DavaodelSur":"MI",
    "DavaoOriental":"MI",
    "DinagatIslands":"MI",
    "EasternSamar":"VI",
    "Guimaras":"VI",
    "Ifugao":"LU",
    "IlocosNorte":"LU",
    "IlocosSur":"LU",
    "Iloilo":"VI",
    "Isabela":"LU",
    "Kalinga":"LU",
    "LaUnion":"LU",
    "Laguna":"LU",
    "LanaodelNorte":"MI",
    "LanaodelSur":"MI",
    "Leyte":"VI",
    "Maguindanao":"MI",
    "Marinduque":"LU",
    "Masbate":"LU",
    "MetropolitanManila":"LU",
    "MisamisOccidental":"MI",
    "MisamisOriental":"MI",
    "MountainProvince":"LU",
    "NegrosOccidental":"VI",
    "NegrosOriental":"VI",
    "NorthCotabato":"MI",
    "NorthernSamar":"VI",
    "NuevaEcija":"LU",
    "NuevaVizcaya":"LU",
    "OccidentalMindoro":"LU",
    "OrientalMindoro":"LU",
    "Palawan":"LU",
    "Pampanga":"LU",
    "Pangasinan":"LU",
    "Quezon":"LU",
    "Quirino":"LU",
    "Rizal":"LU",
    "Romblon":"LU",
    "Samar":"VI",
    "Sarangani":"MI",
    "Siquijor":"VI",
    "Sorsogon":"LU",
    "SouthCotabato":"MI",
    "SouthernLeyte":"VI",
    "SultanKudarat":"MI",
    "Sulu":"MI",
    "SurigaodelNorte":"MI",
    "SurigaodelSur":"MI",
    "Tarlac":"LU",
    "Tawi-Tawi":"MI",
    "Zambales":"LU",
    "ZamboangadelNorte":"MI",
    "ZamboangadelSur":"MI",
    "ZamboangaSibugay":"MI"
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
        # ("AUS", AUS_MAPPER), # Australia
        # ("BRA", BRA_MAPPER), # Brazil
        # ("CAN", CAN_MAPPER), # Canada
        # ("IDN", IDN_MAPPER), # Indonesia
        # ("IND", IND_MAPPER), # India
        # ("JPN", JPN_MAPPER), # Japan
        # ("MYS", MYS_MAPPER), # Malaysia
        ("PHL", PHL_MAPPER), # Philippines
    ]
    
    for country, mapper in data:
        geojson = Path("..","data","geojson",f"gadm41_{country}_1.json")
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
        print(f"{country} shapefile created")
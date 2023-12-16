"""Helper module to create subregions 

This module must be run from the "src/" directory

This module should only be run if shapefiles need to be recreated. All data is originally 
taken from GADM at https://gadm.org/index.html
"""

import geopandas as gpd
import pandas as pd
from typing import Dict, List
import requests
from pathlib import Path 
import zipfile
import shutil
import sys

AUS_MAPPER = {
    # "AshmoreandCartierIslands":"", # non-covered island
    "AustralianCapitalTerritory":"SW",
    # "CoralSeaIslandsTerritory":"", # non-covered island
    "JervisBayTerritory":"SW",
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
    "Goa":"SO",
    "Gujarat":"WE",
    "Haryana":"NO",
    "HimachalPradesh":"NO",
    "JammuandKashmir":"NO",
    "Jharkhand":"EA",
    "Karnataka":"SO",
    "Kerala":"SO",
    # "Lakshadweep":"", # non-covered island 
    "MadhyaPradesh":"WE",
    "Maharashtra":"WE",
    "Manipur":"NE",
    "Meghalaya":"NE",
    "Mizoram":"NE",
    "Nagaland":"NE",
    "NCTofDelhi":"NO",
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
    "Aichi":"CE",
    "Akita":"TO",
    "Aomori":"TO",
    "Chiba":"TO",
    "Ehime":"SH",
    "Fukui":"CE",
    "Fukuoka":"KY",
    "Fukushima":"TO",
    "Gifu":"CE",
    "Gunma":"TO",
    "Hiroshima":"CE",
    "Hokkaido":"HO",
    "Hyōgo":"CE",
    "Ibaraki":"TO",
    "Ishikawa":"CE",
    "Iwate":"TO",
    "Kagawa":"SH",
    "Kagoshima":"KY",
    "Kanagawa":"TO",
    "Kochi":"SH",
    "Kumamoto":"KY",
    "Kyoto":"CE",
    "Mie":"CE",
    "Miyagi":"TO",
    "Miyazaki":"KY",
    "Nagano":"CE",
    "Naoasaki":"KY",
    "Nara":"CE",
    "Niigata":"TO",
    "Oita":"KY",
    "Okayama":"CE",
    "Okinawa":"OK",
    "Osaka":"CE",
    "Saga":"KY",
    "Saitama":"TO",
    "Shiga":"CE",
    "Shimane":"CE",
    "Shizuoka":"CE",
    "Tochigi":"TO",
    "Tokushima":"SH",
    "Tokyo":"TO",
    "Tottori":"CE",
    "Toyama":"CE",
    "Wakayama":"CE",
    "Yamagata":"TO",
    "Yamaguchi":"CE",
    "Yamanashi":"CE",
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

RUS_MAPPER = {
    "Adygey":"SO",
    "Altay":"SI",
    "Amur":"FE",
    "Arkhangel'sk":"NW",
    "Astrakhan'":"CE",
    "Bashkortostan":"UR",
    "Belgorod":"CE",
    "Bryansk":"CE",
    "Buryat":"SI",
    "Chechnya":"SO",
    "Chelyabinsk":"UR",
    "Chukot":"FE",
    "Chuvash":"MV",
    "CityofSt.Petersburg":"NW",
    "Dagestan":"SO",
    "Gorno-Altay":"SI",
    "Ingush":"SO",
    "Irkutsk":"SI",
    "Ivanovo":"CE",
    "Kabardin-Balkar":"SO",
    "Kaliningrad":"NW",
    "Kalmyk":"SO",
    "Kaluga":"CE",
    "Kamchatka":"FE",
    "Karachay-Cherkess":"SO",
    "Karelia":"NW",
    "Kemerovo":"SI",
    "Khabarovsk":"FE",
    "Khakass":"SI",
    "Khanty-Mansiy":"UR",
    "Kirov":"UR",
    "Komi":"NW",
    "Kostroma":"CE",
    "Krasnodar":"SO",
    "Krasnoyarsk":"SI",
    "Kurgan":"UR",
    "Kursk":"CE",
    "Leningrad":"NW",
    "Lipetsk":"CE",
    "Magadan":"FE",
    "Mariy-El":"MV",
    "Mordovia":"MV",
    "MoscowCity":"CE",
    "Moskva":"CE",
    "Murmansk":"NW",
    "Nenets":"NW",
    "Nizhegorod":"CE",
    "NorthOssetia":"SO",
    "Novgorod":"NW",
    "Novosibirsk":"SI",
    "Omsk":"SI",
    "Orel":"CE",
    "Orenburg":"UR",
    "Penza":"MV",
    "Perm'":"UR",
    "Primor'ye":"FE",
    "Pskov":"NW",
    "Rostov":"SO",
    "Ryazan'":"CE",
    "Sakha":"FE",
    "Sakhalin":"FE",
    "Samara":"MV",
    "Saratov":"MV",
    "Smolensk":"CE",
    "Stavropol'":"SO",
    "Sverdlovsk":"UR",
    "Tambov":"CE",
    "Tatarstan":"MV",
    "Tomsk":"SI",
    "Tula":"CE",
    "Tuva":"SI",
    "Tver'":"CE",
    "Tyumen'":"UR",
    "Udmurt":"UR",
    "Ul'yanovsk":"MV",
    "Vladimir":"CE",
    "Volgograd":"CE",
    "Vologda":"CE",
    "Voronezh":"CE",
    "Yamal-Nenets":"UR",
    "Yaroslavl'":"CE",
    "Yevrey":"FE",
    "Zabaykal'ye":"SI",
}

THA_MAPPER = {
    "AmnatCharoen":"NO",
    "AngThong":"CE",
    "BangkokMetropolis":"CE",
    "BuengKan":"NO",
    "BuriRam":"NO",
    "Chachoengsao":"CE",
    "ChaiNat":"CE",
    "Chaiyaphum":"NO",
    "Chanthaburi":"CE",
    "ChiangMai":"NO",
    "ChiangRai":"NO",
    "ChonBuri":"CE",
    "Chumphon":"SO",
    "Kalasin":"NO",
    "KamphaengPhet":"NO",
    "Kanchanaburi":"CE",
    "KhonKaen":"NO",
    "Krabi":"SO",
    "Lampang":"NO",
    "Lamphun":"NO",
    "Loei":"NO",
    "LopBuri":"CE",
    "MaeHongSon":"NO",
    "MahaSarakham":"NO",
    "Mukdahan":"NO",
    "NakhonNayok":"CE",
    "NakhonPathom":"CE",
    "NakhonPhanom":"NO",
    "NakhonRatchasima":"NO",
    "NakhonSawan":"NO",
    "NakhonSiThammarat":"SO",
    "Nan":"NO",
    "Narathiwat":"SO",
    "NongBuaLamPhu":"NO",
    "NongKhai":"NO",
    "Nonthaburi":"CE",
    "PathumThani":"CE",
    "Pattani":"SO",
    "Phangnga":"SO",
    "Phatthalung":"SO",
    "Phayao":"NO",
    "Phetchabun":"NO",
    "Phetchaburi":"CE",
    "Phichit":"NO",
    "Phitsanulok":"NO",
    "PhraNakhonSiAyutthaya":"CE",
    "Phrae":"NO",
    "Phuket":"SO",
    "PrachinBuri":"CE",
    "PrachuapKhiriKhan":"CE",
    "Ranong":"SO",
    "Ratchaburi":"CE",
    "Rayong":"CE",
    "RoiEt":"NO",
    "SaKaeo":"CE",
    "SakonNakhon":"NO",
    "SamutPrakan":"CE",
    "SamutSakhon":"CE",
    "SamutSongkhram":"CE",
    "Saraburi":"CE",
    "Satun":"SO",
    "SiSaKet":"NO",
    "SingBuri":"CE",
    "Songkhla":"SO",
    "Sukhothai":"NO",
    "SuphanBuri":"CE",
    "SuratThani":"SO",
    "Surin":"NO",
    "Tak":"NO",
    "Trang":"SO",
    "Trat":"CE",
    "UbonRatchathani":"NO",
    "UdonThani":"NO",
    "UthaiThani":"NO",
    "Uttaradit":"NO",
    "Yala":"SO",
    "Yasothon":"NO",
}

VNM_MAPPER = {
    "AnGiang":"SO",
    "BàRịa-VũngTàu":"SO",
    "BắcGiang":"NO",
    "BắcKạn":"NO",
    "BạcLiêu":"SO",
    "BắcNinh":"NO",
    "BếnTre":"SO",
    "BìnhĐịnh":"CE",
    "BìnhDương":"SO",
    "BìnhPhước":"SO",
    "BìnhThuận":"CE",
    "CàMau":"SO",
    "CầnThơ":"SO",
    "CaoBằng":"NO",
    "ĐàNẵng":"CE",
    "ĐắkLắk":"CE",
    "ĐắkNông":"CE",
    "ĐiệnBiên":"NO",
    "ĐồngNai":"SO",
    "ĐồngTháp":"SO",
    "GiaLai":"CE",
    "HàGiang":"NO",
    "HàNam":"NO",
    "HàNội":"NO",
    "HàTĩnh":"CE",
    "HảiDương":"NO",
    "HảiPhòng":"NO",
    "HậuGiang":"SO",
    "HồChíMinh":"SO",
    "HoàBình":"NO",
    "HưngYên":"NO",
    "KhánhHòa":"CE",
    "KiênGiang":"SO",
    "KonTum":"CE",
    "LaiChâu":"NO",
    "LâmĐồng":"CE",
    "LạngSơn":"NO",
    "LàoCai":"NO",
    "LongAn":"SO",
    "NamĐịnh":"NO",
    "NghệAn":"CE",
    "NinhBình":"NO",
    "NinhThuận":"CE",
    "PhúThọ":"NO",
    "PhúYên":"CE",
    "QuảngBình":"CE",
    "QuảngNam":"CE",
    "QuảngNgãi":"CE",
    "QuảngNinh":"NO",
    "QuảngTrị":"CE",
    "SócTrăng":"SO",
    "SơnLa":"NO",
    "TâyNinh":"SO",
    "TháiBình":"NO",
    "TháiNguyên":"NO",
    "ThanhHóa":"CE",
    "ThừaThiênHuế":"CE",
    "TiềnGiang":"SO",
    "TràVinh":"SO",
    "TuyênQuang":"NO",
    "VĩnhLong":"SO",
    "VĩnhPhúc":"NO",
    "YênBái":"NO",
}

def make_subregions(geojson: str, country: str, mapper: Dict[str,str], save: str = None) -> gpd.GeoDataFrame:
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
    if country == "IND": # india's borders are tracked a little weird 
        assert (
            (gdf.GID_0 == country) | 
            (gdf.GID_0.str.startswith("Z0"))).all()
    else: 
        assert (gdf.GID_0 == country).all()
    gdf = assign_subregions(gdf, mapper)
    if save:
        gdf.to_file(Path(save,f"{country}.shp"), driver="ESRI Shapefile")
    return gdf
    
def assign_subregions(gdf: gpd.GeoDataFrame, mapper: Dict[str,str]) -> gpd.GeoDataFrame:
    """Assigns subregions to spatial data"""
    
    gdf = gdf[["GID_0", "NAME_1", "geometry"]].rename(columns={"GID_0":"region"})
    gdf["subregion"] = gdf["NAME_1"].map(mapper)
    return gdf.dissolve(by="subregion").reset_index()[["region", "subregion", "geometry"]]

def assign_excluded(gdf: gpd.GeoDataFrame, excluded: List[str] = None) -> gpd.GeoDataFrame:
    """Adds an excluded column to dataframe based on iso codes"""
    
    if excluded:
        gdf["EXCLUDED"] = gdf.apply(
            lambda x: "1" if x.region in excluded else "0", axis=1
        )
    else: 
        gdf["EXCLUDED"] = "0"
    
    # assign geometry column to be at the end
    return gdf[[x for x in gdf.columns if x != "geometry"] + ["geometry"]]

def format_admin_0(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Formats admin level 0 data
    
    https://public.opendatasoft.com/explore/dataset/world-administrative-boundaries/export/
    """

    gdf["subregion"] = "XX"
    return gdf[~(gdf.iso3.isna())][["iso3", "subregion", "geometry"]].rename(columns={"iso3":"region"})

def get_and_extract_zipped_file(url: str, destination: str):
    """Gets and extracts a zipped file from online resource"""
    
    file_name = Path(destination).stem
    download_file(url, f"./{file_name}.zip")
    unzip_file(f"./{file_name}.zip", f"./{file_name}")
    shutil.move(f"./{file_name}/{file_name}.json", destination)
    Path(file_name).rmdir()
    Path(f"{file_name}.zip").unlink()
    

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
    
    # master shapefile 
    shp_file = Path("./","..","data","shapefiles", "world", "world.shp")
    
    if file_exists(shp_file):
        print(f"Spatial representation existis at location {str(shp_file)}")
        print("Exiting...")
        sys.exit()
    
    ###
    # Get base regional representation (admin level 0)
    ###
    
    admin_0_path = Path("..","data","shapefiles", "admin_0", "admin_0.shp")
    
    if not file_exists(admin_0_path):
        geojson_admin_0 = Path("..","data","geojson", "admin_0.geojson")
        if not file_exists(geojson_admin_0):
            
            # gdf_admin_0 = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres")) # futures warning
            download_file(
                url="https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/world-administrative-boundaries/exports/geojson?lang=en&timezone=America%2FLos_Angeles",
                destination=geojson_admin_0
            )
        gdf_admin_0 = format_admin_0(gpd.read_file(geojson_admin_0))
        
        admin_0_path.parent.mkdir(parents=True, exist_ok=True)
        gdf_admin_0.to_file(admin_0_path)
        
        print("Global admin 0 data created")
        
    else:
        gdf_admin_0 = gpd.read_file(admin_0_path)
    
    ###
    # Add subregional representation where required (admin level 1)
    ###
    
    admin_1_data = [
        ("AUS", AUS_MAPPER), # Australia
        ("BRA", BRA_MAPPER), # Brazil
        ("CAN", CAN_MAPPER), # Canada
        ("IDN", IDN_MAPPER), # Indonesia
        ("IND", IND_MAPPER), # India
        ("JPN", JPN_MAPPER), # Japan
        ("MYS", MYS_MAPPER), # Malaysia
        ("PHL", PHL_MAPPER), # Philippines
        ("RUS", RUS_MAPPER), # Russia
        ("THA", THA_MAPPER), # Thailand
        ("VNM", VNM_MAPPER), # Viet Nam
    ]
    
    admin_1_path = Path("..","data","shapefiles", "admin_1", "admin_1.shp")
    if not file_exists(admin_1_path):
        
        admin_1_gdfs = []
        
        for country, mapper in admin_1_data:
            
            geojson = Path("..","data","geojson",f"gadm41_{country}_1.json")
            if not file_exists(geojson):
                get_and_extract_zipped_file(
                    url=f"https://geodata.ucdavis.edu/gadm/gadm4.1/json/{Path(geojson).name}.zip",
                    destination=geojson
                )
                
            admin_1_gdfs.append(
                make_subregions(geojson, country, mapper, save=None)
            )
            
            print(f"{country} data created")
            
        gdf_admin_1 = gpd.pd.concat(admin_1_gdfs, ignore_index=True)
        
        admin_1_path.parent.mkdir(parents=True, exist_ok=True)
        gdf_admin_1.to_file(admin_1_path)
        
    else:
        gdf_admin_1 = gpd.read_file(admin_1_path)
    
    ###
    # Add subregional for USA (balancing authorities)
    ###
    
    usa_path = Path("..","data","shapefiles", "usa", "usa.shp")
    nodes = pd.read_csv(Path("..","data","csv", "nodes.csv"))
    
    if not file_exists(usa_path):
        usa_geojson = Path("..","data","geojson", "usa.geojson")
        if not file_exists(usa_geojson):
            download_file(
                url="https://raw.githubusercontent.com/electricitymaps/electricitymaps-contrib/master/web/geo/world.geojson",
                destination=usa_geojson
            )
        gdf_usa = gpd.read_file(usa_geojson)
        nodes_usa = nodes[nodes.iso == "USA"]
        
        gdf_usa["region"] = "USA"
        gdf_usa = gdf_usa[gdf_usa["countryKey"] == "US"]
        gdf_usa["subregion"] = gdf_usa["zoneName"].map(nodes_usa.set_index("Node_Verbose").to_dict()["region_code"])
        
        # Should only drop Hawaii
        rows_to_drop = gdf_usa[gdf_usa["subregion"].isna()]["zoneName"]
        if not rows_to_drop.empty:
            print(f"Dropping {rows_to_drop.to_list()} from USA dataframe")
        gdf_usa = gdf_usa[~gdf_usa["subregion"].isna()]
        
        gdf_usa = gdf_usa[["region", "subregion", "geometry"]]
        
        usa_path.parent.mkdir(parents=True, exist_ok=True)
        gdf_usa.to_file(usa_path)
        print("Made USA data")
        
    else:
        gdf_usa = gpd.read_file(usa_path)
    
    ### 
    # Create final spatial representation
    ###
    
    excluded_regions = [x for x in gdf_admin_0.region.unique() if x not in nodes.iso.unique()]

    gdf_world = gdf_admin_0[
        ~(gdf_admin_0.region.isin([r[0] for r in admin_1_data])) &
        ~(gdf_admin_0.region == "USA")
    ]
    gdf_world = gpd.pd.concat([gdf_world, gdf_admin_1, gdf_usa], ignore_index=True)
    gdf_world = assign_excluded(gdf_world, excluded_regions)
    
    shp_file.parent.mkdir(parents=True, exist_ok=True)
    gdf_world.to_file(shp_file)
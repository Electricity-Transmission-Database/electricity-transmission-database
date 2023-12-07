'''

    database.py

    Load Global Transmission Database

'''

import os

import pandas as pd
import geopandas as gpd

from shapely.geometry import Point


class GlobalTransmissionDatabase:
    '''Gets all files from: data/global_transmission_database.csv
    '''
    def __init__(
        self,
    ):

        # read nodes
        self._nodes = pd.read_csv(
            '../data/csv/nodes.csv'
        )

        # read iso codes
        self._iso_codes = pd.read_csv(
            '../data/csv/iso_codes.csv'
        )

        # read exclusion zones
        self.INCLUDED_REGIONS = gpd.read_file(
            '../data/shapefiles/excluded_regions/excluded_regions.shp'
        )

        # read database

        ##################
        # PROCESS
        ##################

        # --
        # CENTRE_POINTS
        self.CENTRE_POINTS = self._nodes.copy()

        # map regions
        self.CENTRE_POINTS['region'] = self.CENTRE_POINTS.Node.str[0:3].map( self._iso_codes.set_index('alpha-3')['region'].to_dict() )
        self.CENTRE_POINTS['subregion'] = self.CENTRE_POINTS.Node.str[0:3].map( self._iso_codes.set_index('alpha-3')['sub-region'].to_dict() )

        # convert to geo_df
        geometry = [Point(xy) for xy in zip(self.CENTRE_POINTS.Centroid_Lon, self.CENTRE_POINTS.Centroid_Lat)]
        self.CENTRE_POINTS = self.CENTRE_POINTS.drop(['Centroid_Lon', 'Centroid_Lat'], axis=1)
        self.CENTRE_POINTS = gpd.GeoDataFrame(self.CENTRE_POINTS, crs="EPSG:4326", geometry=geometry)

        # column name
        self.CENTRE_POINTS.columns = [i.lower() for i in self.CENTRE_POINTS.columns]

        # reorder
        self.CENTRE_POINTS = self.CENTRE_POINTS[['node','node_verbose','country','region','subregion','geometry']]

        # --
        # POPULATION_CENTRES
        self.POPULATION_CENTRES = self._nodes.copy()

        # map regions
        self.POPULATION_CENTRES['region'] = self.POPULATION_CENTRES.Node.str[0:3].map( self._iso_codes.set_index('alpha-3')['region'].to_dict() )
        self.POPULATION_CENTRES['subregion'] = self.POPULATION_CENTRES.Node.str[0:3].map( self._iso_codes.set_index('alpha-3')['sub-region'].to_dict() )

        # convert to geo_df
        geometry = [Point(xy) for xy in zip(self.POPULATION_CENTRES.Pop_Lon, self.POPULATION_CENTRES.Pop_Lat)]
        self.POPULATION_CENTRES = self.POPULATION_CENTRES.drop(['Pop_Lon', 'Pop_Lat'], axis=1)
        self.POPULATION_CENTRES = gpd.GeoDataFrame(self.POPULATION_CENTRES, crs="EPSG:4326", geometry=geometry)

        # column name
        self.POPULATION_CENTRES.columns = [i.lower() for i in self.POPULATION_CENTRES.columns]

        # reorder
        self.POPULATION_CENTRES = self.POPULATION_CENTRES[['node','node_verbose','country','region','subregion','population','geometry']]


    def get_something():
        print('todo')
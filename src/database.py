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
        self.DATABASE = pd.read_excel(
            '../data/global_transmission_data.xlsx',
            skiprows=1,
        )

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

        # --
        # DATABASE

        # fix node names
        for c in ['From','To']:

            self.DATABASE.loc[
                self.DATABASE[c].str.len() > 3, c
            ] = self.DATABASE.loc[
                    self.DATABASE[c].str.len() > 3, c
                    ].str[0:3] + '-' + self.DATABASE.loc[
                                self.DATABASE[c].str.len() > 3, c
                                ].str[3:6]

            self.DATABASE.loc[
                self.DATABASE[c].str.len() == 3, c
            ] = self.DATABASE.loc[
                    self.DATABASE[c].str.len() == 3, c
                    ] + '-' + 'XX'
        
        # change column names
        self.DATABASE['Existing Capacity + (MW)'] = self.DATABASE['CAP (MW) +']
        self.DATABASE['Existing Capacity - (MW)'] = self.DATABASE['Cap (MW) -']
        self.DATABASE['Planned Capacity + (MW)']  = self.DATABASE['Cap (MW) +']
        self.DATABASE['Planned Capacity - (MW)']  = self.DATABASE['Cap (MW) -.1']
        
        # drop some columns we don't need
        self.DATABASE = self.DATABASE.drop(
            [
            'Comments', 
            'Name', 
            'Name.1', 
            'Completed?', 
            'Reviewed?', 
            'Technology',
            #'From', 
            #'To', 
            'CAP (MW) +', 
            'Cap (MW) -', 
            'Voltage (kV)',
            'Distance (KM)', 
            'Cap (MW) +', 
            'Cap (MW) -.1', 
            'Voltage (kV) +',
            'Distance (KM).1', 
            #'Year Planned', 
            #'Source Existing (2023)',
            'Source2 Existing (2023)', 
            #'Source Planned', 
            'Source2 Planned',
            #'Assumptions/Applied methods', 
            #'Other Notes', 
            'Unnamed: 23'
            ],
            axis = 1,
        )

        # reorder columns
        self.DATABASE = self.DATABASE[[
            'From',
            'To',
            'Existing Capacity + (MW)',
            'Existing Capacity - (MW)',
            'Planned Capacity + (MW)',
            'Planned Capacity - (MW)',
            'Year Planned',
            'Assumptions/Applied methods',
            'Other Notes',
            'Source Existing (2023)',
            'Source Planned',
        ]]

        # make column names lower case
        self.DATABASE.columns = [i.lower() for i in self.DATABASE.columns]


    def get_interregional_capacity(self,by='subregion'):
        '''Get total capacities (existing and planned) between regions
        '''
        # copy database
        df = self.DATABASE.copy()
        # map region onto nodes
        df['from'] = df['from'].map( self.CENTRE_POINTS.set_index('node')[by].to_dict() )
        df['to'] = df['to'].map( self.CENTRE_POINTS.set_index('node')[by].to_dict() )
        # return sums between different regions
        df = df[df['from'] != df['to']].groupby(by=['from','to']).sum(numeric_only=True).drop('year planned',axis=1)
        # get max of +/- capacity
        for f in ['existing','planned']:
            df[f] = df.filter(regex=f).abs().max(axis=1)
        # return resulting df
        return df[['existing','planned']]
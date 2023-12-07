'''

    dataviz.py

    Make plots from database object

'''

import plotly.express as px

from .database import GlobalTransmissionDatabase

class DatabasePlots:

    def __init__(self
    ):
        self.df = GlobalTransmissionDatabase()

        # setup defaults
        self.default_map_margins = {"r":5,"t":5,"l":5,"b":5}
        self.default_map_height = 400
        self.default_map_width = 800
        self.default_projection_type = "natural earth"


    def excluded_regions(
            self,
            grid=False,
    ):
        '''Show regions included/excluded in the model
        '''

        df = self.df.INCLUDED_REGIONS.set_index('ISO_A3_EH').copy()

        df.loc[df.EXCLUDED == '0', 'EXCLUDED'] = 'Included'
        df.loc[df.EXCLUDED == '1', 'EXCLUDED'] = 'Excluded'

        # make fig
        fig = px.choropleth(
            df,
            geojson=df.geometry,
            locations=df.index,
            color="EXCLUDED",
            color_discrete_map={
                'Included':'navy', 
                'Excluded':'red'
            },
        )

        # update traces
        fig.update_traces(
            marker_line_color='lightgray',
            marker_line_width=0.5,
        )

        # update geos
        fig.update_geos(
            visible=False,
            projection_type=self.default_projection_type,
            lataxis_showgrid=grid, 
            lonaxis_showgrid=grid,
        )

        # set layout
        fig.update_layout(
            height=self.default_map_height, 
            width=self.default_map_width, 
            margin=self.default_map_margins,
            legend_title_text=None,
        )

        return fig
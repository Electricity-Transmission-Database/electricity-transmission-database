'''

    dataviz.py

    Make plots from database object

'''

import math
import numpy as np
import pandas as pd
import networkx as nx
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from matplotlib.lines import Line2D

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
    

    def barplot_lines_by_region(
            self,
            region_col='region',
    ):
        '''Bar plot the number of lines by region
        '''
        pass


    def map_transmission_lines(
            self,
            bins = [0,1,5,10,25],
            labels = ['0-1','1-5','5-10','10-25'],
            planned_capacity = False,
            showgrid = True,
            colours = {
                'node' : 'dimgray',
                'landcolor' : 'whitesmoke',
                'borders' : 'white',
                'oceancolor' : 'white',
                'line_existing' : 'lightcoral',
                'line_planned' : 'navy',
            },
            line_min_width=0.5,
            line_step=1.0,
            show_zero=False,
            **kwargs,
    ):
        '''Plot FEO-Global nodes and edges
        '''

        # load reference data
        nodes = self.df.CENTRE_POINTS.copy()
        links = self.df.DATABASE.copy()

        # # filter out nodes that are not in lines data
        # nodes = nodes.loc[
        #     (nodes.Node.isin(links['from'].tolist())) | \
        #     (nodes.Node.isin(links['to'].tolist()))
        # ]

        # field to plot
        if planned_capacity:
            field_to_plot = 'planned'
        else:
            field_to_plot = 'existing'

        # take midpoint of +/- capacity
        for i in ['existing','planned']:
            links[i] = ( (links[f'{i} capacity + (mw)'].abs() + links[f'{i} capacity - (mw)'].abs()) / 2 ) / 1000 # MW -> GW

        # map lat,lon to links
        links['start_lat'] = links['from'].map( nodes.set_index('node').geometry.y.to_dict() )
        links['start_lon'] = links['from'].map( nodes.set_index('node').geometry.x.to_dict() )
        links['end_lat'] = links['to'].map( nodes.set_index('node').geometry.y.to_dict() )
        links['end_lon'] = links['to'].map( nodes.set_index('node').geometry.x.to_dict() )

        # bin capacities
        links['Capacity_Bin'] = pd.cut(
            links[field_to_plot], 
            bins=bins, 
            labels=labels
        )

        links.Capacity_Bin = links.Capacity_Bin.cat.add_categories(['0'])
        links.Capacity_Bin = links.Capacity_Bin.fillna('0')

        # init fig
        fig = go.Figure()

        # loop through link categories
        link_widths = {}
        for i in labels:
            link_widths[i] = line_min_width
            line_min_width += line_step
        link_widths['0'] = 0

        # remove zero
        if not show_zero:
            links = links[links.Capacity_Bin != '0']

        for i in labels:
            # index dataframe
            idx_links = links.loc[links.Capacity_Bin == i]

            # zip coords
            lons = []
            lats = []
            lons = np.empty(3 * len(idx_links))
            lons[::3] = idx_links['start_lon']
            lons[1::3] = idx_links['end_lon']
            lons[2::3] = None
            lats = np.empty(3 * len(idx_links))
            lats[::3] = idx_links['start_lat']
            lats[1::3] = idx_links['end_lat']
            lats[2::3] = None

            # set names
            name = i + ' GW'
            width = link_widths[i]
            if i == '0':
                color = None
            else:
                if planned_capacity:
                    color = colours['line_planned']
                else:
                    color = colours['line_existing']

            fig.add_trace(
                go.Scattergeo(
                    name=name,
                    lon = lons,
                    lat = lats,
                    mode = 'lines',
                    line = dict(width=width,color=color),
                    opacity = kwargs.get('link_opacity',0.8),
                )
            )

        fig.add_trace(
            go.Scattergeo(
                name='Node',
                lon = nodes.geometry.x,
                lat = nodes.geometry.y,
                hoverinfo = 'text',
                text = nodes['node'] + '<br>' + nodes['country'],
                mode = 'markers',
                showlegend = False,
                marker = dict(
                    opacity = kwargs.get('node_opacity',0.8),
                    size = kwargs.get('node_size',7),
                    color = colours['node'],
                    line = dict(
                        width = 0,
                        color = kwargs.get('node_line_color','DarkSlateGrey'),
                        )
                    )
            )
        )

        fig.update_layout(
            template='ggplot2',
            geo = dict(
                landcolor = colours['landcolor'],
                projection_type=self.default_projection_type,
                showland = True,
                showlakes = False,
                showsubunits = False,
                showcountries = True,
                showcoastlines = False,
                showrivers = False,
                showocean = False,
                oceancolor = colours['oceancolor'],
                countrycolor = colours['borders'],
                resolution = 110,
                lonaxis = dict(
                    showgrid = showgrid,
                    gridwidth = 0.5,
                    dtick = 15
                ),
                lataxis = dict (
                    showgrid = showgrid,
                    gridwidth = 0.5,
                    dtick = 15
                )
                ),
            width=1000,
            height=500,
            margin={"r":50,"t":50,"l":50,"b":50},
            #paper_bgcolor="White",
            showlegend=True,
            legend_title=kwargs.get('legend_title','Key:'),
            title=kwargs.get('title',f'{field_to_plot.title()} capacity (GW)'),
        )

        #plotly_defaults(fig)

        return fig, nodes, links


    def map_excluded_regions(
            self,
            showgrid=False,
            colours={'Included' : 'navy', 'Excluded' : 'red'},
            **kwargs,
    ):
        '''Show regions included/excluded in the model
        '''

        # update exclude column
        df = self.df.INCLUDED_REGIONS.copy()
        df.loc[df.Included == 'True', 'Included'] = 'Included'
        df.loc[df.Included == 'False', 'Included'] = 'Excluded'

        # make fig
        fig = px.choropleth(
            df, 
            locations="alpha-3",
            color="Included", 
            hover_name="name",
            color_discrete_map=colours,
            hover_data=['region','sub-region'],
        )

        # update traces
        fig.update_traces(
            marker_line_color='lightgray',
            marker_line_width=0.5,
            # hovertemplate="<br>".join([
            #     "Country: %{customdata[0]}",
            #     "Region: %{customdata[1]}",
            #     "%{customdata[2]}<extra></extra>"
            # ])
        )

        # update geos
        fig.update_layout(
            title=kwargs.get('title',None),
            template='ggplot2',
            geo = dict(
                landcolor = None,
                projection_type=self.default_projection_type,
                # subunitcolor = "rgb(255, 255, 255)",
                # countrycolor = "rgb(255, 255, 255)",
                lakecolor = "rgb(255, 255, 255)",
                showland = False,
                showlakes = False,
                showsubunits = False,
                showcountries = False,
                showcoastlines = False,
                showrivers = False,
                showocean = False,
                oceancolor = 'white',
                resolution = 110,
                lonaxis = dict(
                    showgrid = showgrid,
                    gridwidth = 0.5,
                    dtick = 15
                ),
                lataxis = dict (
                    showgrid = showgrid,
                    gridwidth = 0.5,
                    dtick = 15
                )
                ),
            width=1000,
            height=500,
            margin={"r":50,"t":50,"l":50,"b":50},
            #paper_bgcolor="White",
            showlegend=True,
            #legend_title=kwargs.get('legend_title','Key:'),
        )

        # set layout
        fig.update_layout(
            height=self.default_map_height, 
            width=self.default_map_width, 
            margin=self.default_map_margins,
            legend_title_text=None,
        )

        return fig


    def network_topology(
            self,
            by='subregion',
            jitter=1,
            colours = {'planned' : 'lightblue', 'existing' : 'orange'},
            font_size=5,
            font_color='white',
            node_size=700,
            figsize=(8,8),
            legend_scale=1,
    ):
        '''Network topology
        '''
        df = self.df.get_interregional_capacity(by=by).copy()

        df = df.reset_index()

        # Generate dict to map positions
        pos_df = self.df.CENTRE_POINTS.groupby(by=by).first().geometry.to_dict()

        # change from/to for labels
        df['from'] = df['from'].str.replace(' ','\n')
        df['to'] = df['to'].str.replace(' ','\n')

        # add source/target
        df['source'] = df['from']
        df['target'] = df['to']

        # add existing to planned
        df['planned'] = df['existing'] + df['planned']

        G = nx.from_pandas_edgelist(
            df,
            edge_attr=["existing", "planned"],
            create_using=nx.MultiGraph(),
        )

        # add positions
        pos = nx.spring_layout(G, seed=7, k=jitter/math.sqrt(G.order()))

        # try:
        #     for n in G.nodes(): 
        #         coords = pos_df[n.replace('\n',' ')].coords[0]

        #         if n == 'Northern\nEurope':
        #             coords = (coords[0]*0.8, coords[1]*1.5)
        #         elif n == 'Western\nEurope':
        #             coords = (coords[0]*-0.8, coords[1])
        #         elif n == 'Eastern\nEurope':
        #             coords = (coords[0]*1.4, coords[1]*1.4)
        #         elif n == 'Central\nAsia':
        #             coords = (coords[0], coords[1]*1.4)
        #         elif n == 'Southern\nAsia':
        #             coords = (coords[0]*1.3, coords[1])
            
        #     pos[n] = coords

        # except:
        #     print('could not configure coords')

        nx.set_node_attributes(G, pos, 'pos')

        # init figure
        fig = plt.figure(figsize=figsize) 

        # nodes
        nx.draw_networkx_nodes(
            G, 
            pos, 
            node_size=node_size,
            node_color='teal',
            alpha=1,
        )

        # edges (planned)
        edgewidth = [ d['planned']/2e3 for (u,v,d) in G.edges(data=True)]

        nx.draw_networkx_edges(
            G, 
            pos, 
            width=edgewidth,
            edge_color=colours['planned'],
            alpha=1,
        )

        # edges (existing)
        edgewidth = [ d['existing']/2e3 for (u,v,d) in G.edges(data=True)]

        nx.draw_networkx_edges(
            G, 
            pos, 
            width=edgewidth,
            edge_color=colours['existing'],
            alpha=1,
        )

        # node labels
        nodelist = G.nodes()
        nx.draw_networkx_labels(
            G, 
            pos,
            labels=dict(zip(nodelist,nodelist)),
            font_color=font_color,
            font_size=font_size,
        )

        # legend
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label=by.title(),markerfacecolor='teal', markersize=5),
            Line2D([0], [0], color=colours['existing'], lw=2, label='Existing capacity (MW)'),   
            Line2D([0], [0], color=colours['planned'], lw=2, label='Planned capacity (MW)'),     
        ]
        plt.legend(handles=legend_elements, loc='upper right', prop={'size': 8*legend_scale}, frameon=False)

        # frame
        plt.box(False)

        return plt
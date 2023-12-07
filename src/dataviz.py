'''

    dataviz.py

    Make plots from database object

'''


import networkx as nx
import plotly.express as px
import matplotlib.pyplot as plt

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
    

    def network_topology(
            self,
            by='subregion'
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
        pos = nx.spring_layout(G, seed=7)

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


        # nodes
        nx.draw_networkx_nodes(
            G, 
            pos, 
            node_size=700,
            node_color='teal',
            alpha=1,
        )

        # edges (planned)
        edgewidth = [ d['planned']/2e3 for (u,v,d) in G.edges(data=True)]

        nx.draw_networkx_edges(
            G, 
            pos, 
            width=edgewidth,
            edge_color='lightblue',
            alpha=1,
        )

        # edges (existing)
        edgewidth = [ d['existing']/2e3 for (u,v,d) in G.edges(data=True)]

        nx.draw_networkx_edges(
            G, 
            pos, 
            width=edgewidth,
            edge_color='orange',
            alpha=1,
        )

        # node labels
        nodelist = G.nodes()
        nx.draw_networkx_labels(
            G, 
            pos,
            labels=dict(zip(nodelist,nodelist)),
            font_color='black',
            font_size=5,
        )

        plt.box(False)
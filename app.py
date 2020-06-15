import dash
import dash_html_components as html
import dash_core_components as dcc
import json
import dash_leaflet as dl
import random
from random import randint
from dash.dependencies import Output, Input
from dash_leaflet import express as dlx
from pandas.io.json import json_normalize
import flask
import os

"""
* Author: Kyle Reinholt
* Date: 6/15/2020
* Purpose: Prototype CU Boulder Campus Density Map Interface
* Prominent Resource Utilized: https://dash-leaflet.herokuapp.com/#us_states
* Notes: Code may be a little messy. Not sure of format conventions in Dash-Python as of (6/15/2020)
"""

#Style for html preview (where the click data is currently being shown) 
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# GIS data was converted to json format to be utilized by dash_leaflet.
with open('assets/buildings.json', 'r') as f:
    data = json.load(f)

# Get Building Capacity Data
# Currently reading in a mock json file with much less data than will be provided in actual system.
# Importantly, the color of the building will be provided in this file. 
with open('assets/building_capacity.json', 'r') as f2:
    capacity = json.load(f2)

#Create dict of building colors from json file
building_colors = {}
for building in capacity["buildings"]:
    building_colors[building["buildingName"]]=building["color"]
    
# Lists for colorbar creation (bottom left of map) 
marks = [0, 1, 2]
colorscale = ['#008000', '#FD8D3C', '#E31A1C']

# Assign building color from dictionary { "buildingName" : "color" }  
def getColor(bName):
    color = building_colors["'"+bName+"'"].replace("'","")
    return color

# Sets the style of each building, called by dlx.geojson()
def get_style(feature):
    return dict(fillColor=getColor(feature["properties"]["name"]), weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)

# Utilized by the hover callback to display the building name. 
def get_info(feature=None):
    header = [html.H2("Building")]
    if not feature:
        return header + ["Hoover over a building"]
    return header + [html.B(feature["properties"]["name"]), html.Br()]

# Create colorbar.
ctg = ["{}+".format(mark, marks[i + 1]) for i, mark in enumerate(marks[:-1])] + ["{}+".format(marks[-1])]
colorbar = dlx.categorical_colorbar(categories=["Below Capacity", "Near Capacity", "Above Capacity"], colorscale=colorscale, width=300, height=30, position="bottomleft")
# Create geojson.
options = dict(hoverStyle=dict(weight=5, color='#666', dashArray=''), zoomToBoundsOnClick=True)
geojson = dlx.geojson(data, id="geojson", defaultOptions=options, style=get_style)
# Create info control.
info = html.Div(children=get_info(), id="info", className="info",
                style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1000", "background":"white"})
# Create app.
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)
app.layout = html.Div([html.H1("CU Boulder Density Map"),dl.Map(children=[dl.TileLayer(), geojson, colorbar, info], center=[40.006, -105.266], zoom=16),html.Div(className='row', children=[
        html.Div([
            dcc.Markdown("""
                **Click Data**
            """),
            html.Pre(id='click-data', style=styles['pre'])
        ], className='three columns')
    ])],
    style={'width': '60%', 'height': '50vh', 'margin': "auto", "display": "block", "font-weight": "bold"})

#On hover, we display the name of the building
@app.callback(Output("info", "children"), [Input("geojson", "featureHover")])
def info_hover(feature):
    return get_info(feature)

#Prints building id when clicked. The id was set in the original gis data file. Printing "something" to show that the information can be accessed. 
@app.callback(
    Output('click-data', 'children'),
    [Input('geojson', 'featureClick')])
def display_click_data(feature):
    return feature["id"]

if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)

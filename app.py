import dash
import dash_html_components as html
import dash_core_components as dcc
import json
import dash_leaflet as dl
import random
from dash.dependencies import Output, Input
from dash_leaflet import express as dlx
from pandas.io.json import json_normalize
import plotly.graph_objs as go
import numpy as np
import datetime 
import calendar
import os
from random import randint
  
def findDay(date):
    date = date.replace("-"," ")
    born = datetime.datetime.strptime(date, '%d %m %Y').weekday() 
    return (calendar.day_name[born].replace("day","") +'\n' + date.replace("2020","20")) 

with open('assets/time.json', 'r') as f:
    data3 = json.load(f)

flag = 0

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
    },
    'space': {
        'padding':'40px'
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

def getBuildingData(bName):
    global data3
    datesList = []
    filteredDates = []
    xs = []
    ys = []
    for line in data3:
        if line["building"] in bName:
            print("building found")
            for d in line["dates"]:
                #print(d["date"])
                datesList.append(d["date"])
                
            sortedDates = sorted(datesList, key=lambda f: tuple(map(int, f.split('-'))))
            for day in sortedDates:
                if "05-2020" in day:
                    continue
                else:
                    filteredDates.append(day)

        for day in filteredDates:
            if line["building"] in bName:
                xs.append(findDay(day))
                for d in line["dates"]:
                    times = []
                    sortedTimes = []
                    if day == d["date"]:
                        #print(d["date"])
                        for t in d["times_list"]:
                            times.append(t["time"])
                        sortedTimes = sorted(times, key=lambda f: tuple(map(int, f.split(':'))))

                        for time in sortedTimes:
                            for t in d["times_list"]:
                                if time == t["time"]:
                                    #xs.append(time)
                                    ys.append(t["density"]*100)
    fig = go.Figure(data=go.Scatter(x=xs, y=ys))
    med = np.median(ys)
    fig.update_layout(title=bName + " Density over Time",shapes=[
    dict(
      type= 'line',
      yref= 'paper', y0=med, y1= med,
      xref= 'x', x0= -1, x1= len(xs)
        )
    ])
    

    return  html.Div(
            dcc.Graph(
                id='scatter',
                figure=fig))
    

# Assign building color from dictionary { "buildingName" : "color" }  
def getColor(bName):
    color = building_colors["'"+bName+"'"].replace("'","")
    return color

def getColor2(bName):
    color = '#008000'
    return color

# Sets the style of each building, called by dlx.geojson()
def get_style(feature):
    return dict(fillColor=getColor(feature["properties"]["name"]), weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)

def get_style2(feature):
    return dict(fillColor=getColor2(feature["properties"]["name"]), weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)

# Utilized by the hover callback to display the building name. 
def get_info(feature=None):
    header = [html.H2("Building")]
    if not feature:
        return header + ["Hover over a building"]
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
app = dash.Dash(prevent_initial_callbacks=True)
app.layout = html.Div([html.H1("CU Boulder Density Map 2020"),dl.Map(id="map", children=[dl.TileLayer(), geojson, colorbar, info], center=[40.006, -105.266], zoom=16),
                       dcc.Slider(
        id='my-slider',
        min=0,
        max=10,
        step=None,
        marks={
        0: 'Fri 6/12',
        3: 'Sat 6/13',
        5: 'Sun 6/14',
        7.65: 'Mon 6/15',
        10: 'Tues 6/16'
        },
        value=10
    ),
    html.Div(id='slider-output-container'),html.Div(
                id='cx1'
                )],
    style={'width': '60%', 'height': '50vh', 'margin': "auto", "display": "block", "font-weight": "bold"})

#On hover, we display the name of the building
@app.callback(Output("info", "children"), [Input("geojson", "featureHover")])
def info_hover(feature):
    return get_info(feature)

#Prints building id when clicked. The id was set in the original gis data file. Printing "something" to show that the information can be accessed. 
"""
@app.callback(
    Output('map', 'children'),
    [Input('geojson', 'featureClick')])
def display_click_data2(feature):
    if not feature:
        return
    return mapUpdate
"""

@app.callback(
    Output('cx1', 'children'),
    [Input('geojson', 'featureClick')])
def display_click_data(feature):
    return getBuildingData(feature["properties"]["name"])
"""
@app.callback(
    dash.dependencies.Output('slider-output-container', 'children'),
    [dash.dependencies.Input('my-slider', 'value')])
def update_output(value):
    return 'You have selected "{}"'.format(value)
"""
@app.callback(
    dash.dependencies.Output('map', 'children'),
    [dash.dependencies.Input('my-slider', 'value')])
def update_output(value):
    global flag
    mapUpdate= [] 
    if flag == 0: 
        ctg = ["{}+".format(mark, marks[i + 1]) for i, mark in enumerate(marks[:-1])] + ["{}+".format(marks[-1])]
        colorbar = dlx.categorical_colorbar(categories=["Below Capacity", "Near Capacity", "Above Capacity"], colorscale=colorscale, width=300, height=30, position="bottomleft")
        options = dict(hoverStyle=dict(weight=5, color='#666', dashArray=''), zoomToBoundsOnClick=True)
        geojson = dlx.geojson(data, id="geojson", defaultOptions=options, style=get_style2)
        info = html.Div(children=get_info(), id="info", className="info",
        style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1000", "background":"white"})
        mapUpdate = [dl.TileLayer(), geojson, colorbar, info]
        flag = 1
    else:
        ctg = ["{}+".format(mark, marks[i + 1]) for i, mark in enumerate(marks[:-1])] + ["{}+".format(marks[-1])]
        colorbar = dlx.categorical_colorbar(categories=["Below Capacity", "Near Capacity", "Above Capacity"], colorscale=colorscale, width=300, height=30, position="bottomleft")
        options = dict(hoverStyle=dict(weight=5, color='#666', dashArray=''), zoomToBoundsOnClick=True)
        geojson = dlx.geojson(data, id="geojson", defaultOptions=options, style=get_style)
        info = html.Div(children=get_info(), id="info", className="info",
        style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1000", "background":"white"})
        mapUpdate = [dl.TileLayer(), geojson, colorbar, info]
        flag = 0
    return mapUpdate


if __name__ == '__main__':
    app.run_server()

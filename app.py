import dash
import dash_html_components as html
import dash_core_components as dcc
import json
import dash_leaflet as dl
import random
from dash.dependencies import Output, Input
from dash_leaflet import express as dlx
from pandas.io.json import json_normalize
import plotly.graph_objects as go
import numpy as np
import datetime 
import calendar
import flask
import os
from random import randint

currentDate = ""
currentValue = 0
lastBuilding =""
  
def findDay(date):
    date = date.replace("-"," ")
    born = datetime.datetime.strptime(date, '%d %m %Y').weekday() 
    return (calendar.day_name[born].replace("day","") +'\n' + date.replace("2020","20")) 

with open('assets/time.json', 'r') as f:
    data3 = json.load(f)

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

colorscale = [
    "#63d3ff",
"#30b7f1",
"#009be3",
"#007fd3",
"#0062c0",
"#0046aa",
"#002891",
"#020175"
    ]

def getColorFromDensity(bName,date):
    global data3
    global colorscale
    color = ""
    datesList = []
    filteredDates = []
    xs = []
    ys = []
    for line in data3:
        if line["building"] in bName:
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
            if date == day:
                if line["building"] in bName:
                    xs.append(findDay(day))
                    for d in line["dates"]:
                        times = []
                        sortedTimes = []
                        #if day == d["date"]:
                        #print(day,date)
                        if date == d["date"]:
                            #print(d["date"])
                            for t in d["times_list"]:
                                times.append(t["time"])
                            sortedTimes = sorted(times, key=lambda f: tuple(map(int, f.split(':'))))

                            for time in sortedTimes:
                                for t in d["times_list"]:
                                    if time == t["time"]:
                                        #xs.append(time)
                                        #ys.append(t["density"]*100)
                                        ys.append(int(t["occupancy"]))
    if(len(ys) <= 2):
        color = "#A9A9A9"
    else:
        maxDensityForDay = np.max(ys)
        if maxDensityForDay >= 35:
            color = colorscale[7]
        elif maxDensityForDay < 35 and maxDensityForDay >= 30:
            color = colorscale[6]
        elif maxDensityForDay < 30 and maxDensityForDay >= 25:
            color = colorscale[5]
        elif maxDensityForDay < 25 and maxDensityForDay >= 20:
            color = colorscale[4]
        elif maxDensityForDay < 20 and maxDensityForDay >= 15:
            color = colorscale[3]
        elif maxDensityForDay < 15 and maxDensityForDay >= 10:
            color = colorscale[2]
        elif maxDensityForDay < 10 and maxDensityForDay >= 5:
            color = colorscale[1]
        else:
            color = colorscale[0]

    return color

def getX(val):
    global currentValue
    if val == 1:
        currentValue = 0
    elif val == 2:
        currentValue = 1
    elif val == 3:
        currentValue = 2
    elif val == 4:
        currentValue = 3
    elif val == 5:
        currentValue = 4
    elif val == 6:
        currentValue = 5
    elif val == 7:
        currentValue = 6
    elif val == 8:
        currentValue = 7
    elif val == 9:
        currentValue = 8
    elif val == 10:
        currentValue = 9
    elif val == 11:
        currentValue = 10
    elif val == 12:
        currentValue = 11
    elif val == 13:
        currentValue = 12
    elif val == 14:
       currentValue = 13
    elif val == 15:
        currentValue = 14
    elif val == 16:
        currentValue = 15

def setDate(val):
    global currentDate
    if val == 1:
        currentDate = "01-06-2020"
    elif val == 2:
        currentDate = "02-06-2020"
    elif val == 3:
        currentDate = "03-06-2020"
    elif val == 4:
        currentDate = "04-06-2020"
    elif val == 5:
        currentDate = "05-06-2020"
    elif val == 6:
        currentDate = "06-06-2020"
    elif val == 7:
        currentDate = "07-06-2020"
    elif val == 8:
        currentDate = "08-06-2020"
    elif val == 9:
        currentDate = "09-06-2020"
    elif val == 10:
        currentDate = "10-06-2020"
    elif val == 11:
        currentDate = "11-06-2020"
    elif val == 12:
        currentDate = "12-06-2020"
    elif val == 13:
        currentDate = "13-06-2020"
    elif val == 14:
        currentDate = "14-06-2020"
    elif val == 15:
        currentDate = "15-06-2020"
    elif val == 16:
        currentDate = "16-06-2020"

def getBuildingData(bName):
    global data3
    global currentValue
    datesList = []
    filteredDates = []
    xs = []
    #ys = []
    meanYs = []
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
                ys =[]
                if(findDay(day) in xs):
                   pass
                else: 
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
                                        #ys.append(t["density"])
                                        ys.append(int(t["occupancy"]))

                    meanYs.append(np.max(ys))

    fig = go.Figure(data=go.Scatter(x=xs, y=meanYs))
    #med = np.median(ys)
    fig.update_layout(title=bName + " Occupancy over Time")
    

    return  html.Div(
            dcc.Graph(
                id='scatter',
                figure=fig))

def getBuildingData2(bName,val):
    global data3
    global currentValue
    datesList = []
    filteredDates = []
    xs = []
    #ys = []
    meanYs = []
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
                ys =[]
                if(findDay(day) in xs):
                   pass
                else: 
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
                                        #ys.append(t["density"])
                                        ys.append(int(t["occupancy"]))

                    meanYs.append(np.max(ys))

    fig = go.Figure(data=go.Scatter(x=xs, y=meanYs))
    fig.update_layout(title=bName + " Occupancy over Time")
    #med = np.median(ys)

    #Uncomment for threshold
    """
    fig.add_trace(go.Scatter(
        x=[xs[int(len(xs)/2)-1]],
        y=[29],
        text=["Occupancy Threshold"],
        mode="text",
    ))"""
    fig.update_layout(title=bName + " Occupancy over Time",shapes=[
    dict(
      type= 'line',
      yref= 'y', y0=0, y1=np.max(meanYs)+5,
      xref= 'x', x0= xs[val], x1= xs[val],
       line=dict(
                color="blue",
                width=4,
                dash="dashdot",
            )
        )
    ])
    
    #Uncomment for threshold
    """
    fig.add_trace(go.Scatter(
        x=[xs[int(len(xs)/2)-1]],
        y=[29],
        text=["Occupancy Threshold"],
        mode="text",
    ))
    fig.update_layout(title=bName + " Occupancy over Time",shapes=[
    dict(
      type= 'line',
      yref= 'y', y0=30, y1=30,
      xref= 'x', x0= -1, x1= len(xs),
       line=dict(
                color="Red",
                width=4,
                dash="dashdot",
            )
        )
    ])
    """

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
    return dict(fillColor=getColorFromDensity(feature["properties"]["name"],"16-06-2020"), weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.9)

def get_style2(feature):
    return dict(fillColor=getColorFromDensity(feature["properties"]["name"],currentDate), weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.9)

# Utilized by the hover callback to display the building name. 
def get_info(feature=None):
    header = [html.H2("Building")]
    if not feature:
        return header + ["Hover over a building"]
    return header + [html.B(feature["properties"]["name"]), html.Br()]

# Create colorbar.
ctg = ["{}+".format(mark, marks[i + 1]) for i, mark in enumerate(marks[:-1])] + ["{}+".format(marks[-1])]
colorbar = dlx.categorical_colorbar(categories=["0+", "5+", "10+","15+","20+","25+","30+","35+"], colorscale=colorscale, width=300, height=30, position="bottomleft")
# Create geojson.
options = dict(hoverStyle=dict(weight=5, color='#666', dashArray=''), zoomToBoundsOnClick=True)
geojson = dlx.geojson(data, id="geojson", defaultOptions=options, style=get_style)
# Create info control.
info = html.Div(children=get_info(), id="info", className="info",
                style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1000"})
# Create app.
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)
app.layout = html.Div([html.H1("CU Boulder Occupancy Map 2020"),dl.Map(id="map", children=[dl.TileLayer(), geojson, colorbar, info], center=[40.006, -105.266], zoom=16),
                       dcc.Slider(
        id='my-slider',
        min=0,
        max=17,
        step=None,
        marks={
        1: 'Mon 01-06',
        2: 'Tue 02-06',
        3: 'Wed 03-06',
        4: 'Thu 04-06',
        5: 'Fri 05-06',
        6: 'Sat 06-06',
        7: 'Sun 07-06',
        8: 'Mon 08-06',
        9: 'Tue 09-06',
        10: 'Wed 10-06',
        11: 'Thu 11-06',
        12: 'Fri 12-06',
        13: 'Sat 13-06',
        14: 'Sun 14-06',
        15: 'Mon 15-06',
        16: 'Tue 16-06'
        },
        value=16
    ),
    html.Div(id='slider-output-container'),html.Div(
                id='cx1'
                ),html.Div(id='txt')],
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
    [Input('geojson', 'featureClick'),
     Input('my-slider','value')])
def display_click_data(feature,value):
    global lastBuilding
    if not feature:
        return getBuildingData2(lastBuilding,value-1)
    if not value:
        lastBuilding = feature["properties"]["name"]
        return getBuildingData(feature["properties"]["name"])
    #getX(value)
    
    return getBuildingData2(feature["properties"]["name"],value-1)

"""
@app.callback(
    dash.dependencies.Output('cx1', 'children'),
    [dash.dependencies.Input('my-slider', 'value')])
def add_vertical_line(value):
    return 

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
    mapUpdate= [] 
    setDate(value)
    ctg = ["{}+".format(mark, marks[i + 1]) for i, mark in enumerate(marks[:-1])] + ["{}+".format(marks[-1])]
    colorbar = dlx.categorical_colorbar(categories=["0+", "5+", "10+","15+","20+","25+","30+","35+"], colorscale=colorscale, width=300, height=30, position="bottomleft")
    options = dict(hoverStyle=dict(weight=5, color='#666', dashArray=''), zoomToBoundsOnClick=True)
    geojson = dlx.geojson(data, id="geojson", defaultOptions=options, style=get_style2)
    info = html.Div(children=get_info(), id="info", className="info",
    style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1000", "background":"white"})
    mapUpdate = [dl.TileLayer(), geojson, colorbar, info]
  
    return mapUpdate


if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)

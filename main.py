from utils import VideoCamera, gen
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
from dash import dcc, html, dash_table
from flask import Flask, Response
import plotly.graph_objects as go
from pymongo import MongoClient
import plotly.express as px
from bson import ObjectId
import dash_daq as daq
import pandas as pd
import serial
import dash
import cv2

from serializer import serialPort 

host         = '127.0.0.1'
port         =  27017
databasename = 'flora_data'

client     = MongoClient(host, port)
database   = client[databasename]
collection = database.telemetry

ser = serialPort()

server = Flask(__name__)
app = dash.Dash(
    __name__, 
    server=server,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

df   = pd.DataFrame(list(collection.find()))
df   = df.iloc[:, 1:]
data = df.to_dict('records')

def Header(name, app):
    title = html.H2(name, style={"margin-top": 5})
    parag = html.P('Process control and reporting')
    logo = html.Img(
        src=app.get_asset_url("flora-logo.png"), style={"height": 80}
    )
    return dbc.Row([dbc.Col([title,parag], class_name='p-2', md=12)])

graphs = [
    [dcc.Graph(id="temperature_graph", figure=px.line(data, x='date_time', y='temperature', title="Temperature"))],
    [dcc.Graph(id="humidity_graph", figure=px.line(data, x='date_time', y='humidity',    title="Humidity"))],
    [dcc.Graph(id="soilmoisture_graph", figure=px.line(data, x='date_time', y='soilmoisture',title="Soil moisture"))],
    [dcc.Graph(id="C02_graph", figure=px.line(data, x='date_time', y='soilmoisture',title="CO2 level"))]
]

cards = [
    dbc.Card(
        [
            html.H2(f"{df.iloc[-1].temperature} °", className="card-title"),
            html.P("Temperature", className="card-text"),
        ],
        body=True,
        color="light",
    ),
    dbc.Card(
        [
            html.H2(f"{df.iloc[-1].humidity} %", className="card-title"),
            html.P("Humidity", className="card-text"),
        ],
        body=True,
        color="success",
        inverse=True,
    ),
    dbc.Card(
        [
            html.H2(f"{df.iloc[-1].soilmoisture} ", className="card-title"),
            html.P("Soil moisture", className="card-text"),
        ],
        body=True,
        color="dark",
        inverse=True,
    ),
    dbc.Card(
        [
            html.H2("400 ppm", className="card-title"),
            html.P("C02 level", className="card-text"),
        ],
        body=True,
        color="primary",
        inverse=True,
    ),
]

sidebar = html.Div(
    [
        html.H2("Flora", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Monitoring", href="/", active="exact"),
                dbc.NavLink("Analytics", href="/analytics", active="exact"),
                dbc.NavLink("Database", href="/database", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "12rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa"
    }
)


app.layout = dbc.Container(
    [   
        sidebar,
        Header("Greenhouse plant monitoring dashboard", app),
        dbc.Row([dbc.Col(card, width=3) for card in cards]),
        
    ],
    fluid=True,
    style={
        "margin-left": "12rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"

    },
    id="page-content",
    class_name="w-auto"
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return ''
    elif pathname == "/analytics":
        return ''
    elif pathname == "/database":
        return ''
    elif pathname == "/control":
        return ''
   
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

@server.route('/video_feed/1')
def video_feed_1():
    camera_idx1 = VideoCamera(0)
    return Response(gen(camera_idx1), mimetype='multipart/x-mixed-replace; boundary=frame')

@server.route('/video_feed/2')
def video_feed_2():
    camera_idx2 = VideoCamera(2)
    return Response(gen(camera_idx2), mimetype='multipart/x-mixed-replace; boundary=frame')

@server.route('/video_feed/3')
def video_feed_3():
    camera_idx3 = VideoCamera(1)
    return Response(gen(camera_idx3), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run_server(debug=True,port=8080,host='0.0.0.0')
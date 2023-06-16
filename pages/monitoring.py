import sys

sys.path.append('../utils')

from dash import html, dcc, callback, Input, Output
from dash.dependencies import Input, Output, State
from utils.database_handle import DataBaseClient
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from utils.serializer import serialPort 
from flask import Flask, Response
import plotly.express as px
import dash_daq as daq
import pandas as pd
import dash
import cv2



dash.register_page(__name__, path='/')

dbclient   = DataBaseClient()
collection = dbclient.get_all_records()

df   = pd.DataFrame(list(collection.find()))
df   = df.iloc[:, 1:]
data = df.to_dict('records')

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

graphs = [
    [dcc.Graph(id="temperature_graph", figure=px.line(data, x='date_time', y='temperature', title="Temperature"))],
    [dcc.Graph(id="humidity_graph", figure=px.line(data, x='date_time', y='humidity',    title="Humidity"))],
    [dcc.Graph(id="soilmoisture_graph", figure=px.line(data, x='date_time', y='soilmoisture',title="Soil moisture"))],
    [dcc.Graph(id="C02_graph", figure=px.line(data, x='date_time', y='co2',title="CO2 level"))]
]

layout = html.Div(
    children=[
        dbc.Row([dbc.Col(card, width=3) for card in cards]),
        dbc.Row([dbc.Col(graph, width=12) for graph in graphs])
    ]
)
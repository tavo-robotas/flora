import sys

sys.path.append('../utils')

from dash import html, dcc, callback, Input, Output
from utils.database_handle import DataBaseClient
from utils.serializer import serialPort 
from utils.camera_stream  import VideoCamera, gen 
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flask import Flask, Response
import plotly.express as px
import dash_daq as daq
import pandas as pd
import dash
import cv2

ser = serialPort()

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
tabs  = dbc.Tabs(
    [
        dbc.Tab(label="data plots", tab_id="data_plots"),
        dbc.Tab(label="vision",     tab_id="camere_feed"),
        dbc.Tab(label="control",    tab_id="control_panel")
    ],
    id="data_tabs",
    active_tab="data_plots",
)
controllers = [
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.H5("Fan", className="card-title float-start"),
                    dbc.Badge("",id='fan-output',  className="ms-1")
                ])   
            ]),
            dbc.Row([
                dbc.Col([
                    daq.BooleanSwitch(id='fan', style={'display': 'flex'}, className='p-0', on=False, persistence=True)
                 ])
            ])
        ]
    ),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.H5("Water", className="card-title float-start"),
                    dbc.Badge("",id='water_pump-output',  className="ms-1")
                ])   
            ]),
            dbc.Row([
                dbc.Col([
                    daq.BooleanSwitch(id='water_pump', style={'display': 'flex'}, className='p-0', on=False, persistence=True)
                 ])
            ])
        ]
    ),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.H5("Lights", className="card-title float-start"),
                    dbc.Badge("",id='lights-output',  className="ms-1")
                ])   
            ]),
            dbc.Row([
                dbc.Col([
                    daq.BooleanSwitch(id='lights', style={'display': 'flex'}, className='p-0', on=False, persistence=True)
                 ])
            ])
        ]
    ),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.H5("Air", className="card-title float-start"),
                    dbc.Badge("",id='ventilation-output',  className="ms-1")
                ])   
            ]),
            dbc.Row([
                dbc.Col([
                    daq.BooleanSwitch(id='ventilation', style={'display': 'flex'}, className='p-0', on=False, persistence=True)
                 ])
            ])
        ]
    ),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.H5("Portal", className="card-title float-start"),
                    dbc.Badge("",id='portal_power-output',  className="ms-1")
                ])   
            ]),
            dbc.Row([
                dbc.Col([
                    daq.BooleanSwitch(id='portal_power', style={'display': 'flex'}, className='p-0', on=False, persistence=True)
                 ])
            ])
        ]
    )    
]
sections = [
    html.Div(
        [
            html.H4("camera idx:1", className="display-6 fw-bold"),
            html.Hr(className="my-2"),
            html.Img(src="/video_feed/1", className="mh-100 w-100 h-auto"),
            html.P(
                "View description {plant}, {location}, {channel}"
            ),
            html.Div([
                dbc.Button("Settings", id="open-centered"),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Camera idx:1 settings"), close_button=True),
                        dbc.ModalBody(
                            html.Div([
                                daq.Slider(
                                    max=100,
                                    size=400,
                                    id='my-daq-slider-ex-1',
                                    value=17
                                ),
                                html.Div(id='slider-output-1')
                            ])
                        ),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close",
                                id="close-centered",
                                className="ms-auto",
                                n_clicks=0,
                            )
                        ),
                    ],
                    id="modal-centered",
                    centered=True,
                    is_open=False,
                )
            ])
        ],
        className="h-100 p-5  bg-light rounded-3"
    ),
    html.Div(
        [
            html.H4("camera idx:2", className="display-6 fw-bold"),
            html.Hr(className="my-2"),
            html.Img(src="/video_feed/2", className="mh-100 w-100 h-auto"),
            html.P(
                "View description {plant}, {location}, {channel}"
            ),
            dbc.Button("Settings", color="primary", className="lead"),
        ],
        className="h-100 p-5 bg-light rounded-3"
    ),
    html.Div(
        [
            html.H4("camera idx:3", className="display-6 fw-bold"),
            html.Hr(className="my-2"),
            html.Img(src="/video_feed/3", className="mh-100 w-100 h-auto"),
            html.P(
                "View description {plant}, {location}, {channel}"
            ),
            dbc.Button("Settings", color="primary", className="lead"),
        ],
        className="h-100 p-5 bg-light rounded-3"
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
        html.Br(),
        dbc.Row(dbc.Col(tabs)),
        html.Div(id="tab-content")
    ]
)

def cmd_rcv(state, msg):
    payload = msg.encode()
    ser.flush()
    ser.writer(payload)
    val = ser.reader()  
    if val is None:
        raise PreventUpdate
    else:
        return f'{val}'

@callback(
    Output("tab-content", "children"),
    Input("data_tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab is not None:
        if active_tab == "data_plots":
            return[dbc.Row(dbc.Col(graph)) for graph in graphs]
        elif active_tab == "camere_feed":
            return dbc.Row([dbc.Col(section, class_name="m-2 md-6") for section in sections], class_name='align-items-md-stretch')
        elif active_tab == "control_panel":
            return dbc.Row([dbc.Col(dbc.Card(control), class_name="m-2") for control in controllers])

    return "No tab selected"

@callback(
    Output("modal-centered", "is_open"),
    [Input("open-centered", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@callback(
    Output('fan-output', 'children'),
    Input('fan', 'on')
)
def update_output(state):
    msg = "fan on" if state else "fan off"
    return cmd_rcv(state, msg)


@callback(
    Output('water_pump-output', 'children'),
    Input('water_pump', 'on')
)
def update_output(state):
    msg = "water pump on" if state else "water pump off"
    return cmd_rcv(state, msg)

@callback(
    Output('lights-output', 'children'),
    Input('lights', 'on')
)
def update_output(state):
    msg = "lights on" if state else "lights off"
    return cmd_rcv(state, msg)

@callback(
    Output('ventilation-output', 'children'),
    Input('ventilation', 'on')
)
def update_output(state):
    msg = "ventilation on" if state else "ventilation off"
    return cmd_rcv(state, msg)

@callback(
    Output('portal_power-output', 'children'),
    Input('portal_power', 'on')
)
def update_output(state):
    msg = "portal on" if state else "portal off"
    return cmd_rcv(state, msg)

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

tabs  = dbc.Tabs(
    [
        dbc.Tab(label="data plots", tab_id="data_plots"),
        dbc.Tab(label="vision", tab_id="camere_feed"),
        dbc.Tab(label="control", tab_id="control_panel")
    ],
    id="data_tabs",
    active_tab="data_plots",
)

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
        html.Br(),
        dbc.Row(dbc.Col(tabs)),
        html.Div(id="tab-content")
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

controllers = [
    dbc.CardBody(
        [  
            html.H5("Fan", className="card-title"),
            html.Div([
                daq.BooleanSwitch(id='fan', on=False, persistence=True),
                html.Div(id='fan-output')
            ], className="float-start")
        ]
    ),
    dbc.CardBody(
        [
            html.H5("Watering", className="card-title"),
            html.Div([
                daq.BooleanSwitch(id='water_pump', on=False, persistence=True),
                html.Div(id='water_pump-output')
            ], className="float-start")
        ]
    ),
    dbc.CardBody(
        [
            html.H5("Lights", className="card-title"),
            html.Div([
                daq.BooleanSwitch(id='lights', on=False, persistence=True),
                html.Div(id='lights-output')
            ], className="float-start")
        ]
    ),
    dbc.CardBody(
        [
            html.H5("Ventilation", className="card-title"),
            html.Div([
                daq.BooleanSwitch(id='ventilation', on=False, persistence=True),
                html.Div(id='ventilation-output')
            ], className="float-start")
        ]
    ),
    dbc.CardBody(
        [
            html.H5("Portal", className="card-title"),
            html.Div([
                daq.BooleanSwitch(id='portal_power', on=False, persistence=True),
                html.Div(id='portal_power-output')
            ], className="float-start")
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

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return ''
    elif pathname == "/analytics":
        return ''
    elif pathname == "/database":
        return ''
   
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

@app.callback(
    Output("modal-centered", "is_open"),
    [Input("open-centered", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output('fan-output', 'children'),
    Input('fan', 'on')
)
def update_output(state):
    if state is True:
        msg = "fan on"
        payload = msg.encode()
        ser.flush()
        ser.write(payload)
    

    if state is False:
        msg = "fan off"
        payload = msg.encode()
        ser.flush()
        ser.write(payload)
    return ''

@app.callback(
    Output('water_pump-output', 'children'),
    Input('water_pump', 'on')
)
def update_output(state):
    if state is True:
        msg = "water pump on"
        payload = msg.encode()
        ser.flush()
        ser.write(payload)
    

    if state is False:
        msg = "water pump off"
        payload = msg.encode()
        ser.flush()
        ser.write(payload)
    return ''

@app.callback(
    Output('lights-output', 'children'),
    Input('lights', 'on')
)
def update_output(state):
    if state is True:
        msg = "lights on"
        payload = msg.encode()
        ser.flush()
        ser.write(payload)
    

    if state is False:
        msg = "lights off"
        payload = msg.encode()
        ser.flush()
        ser.write(payload)
    return ''

@app.callback(
    Output('ventilation-output', 'children'),
    Input('ventilation', 'on')
)
def update_output(state):
    if state is True:
        msg = "ventilation on"
        payload = msg.encode()
        ser.flush()
        ser.write(payload)
    

    if state is False:
        msg = "ventilation off"
        payload = msg.encode()
        ser.flush()
        ser.write(payload)
    return ''

@app.callback(
    Output('portal_power-output', 'children'),
    Input('portal_power', 'on')
)
def update_output(state):
    if state is True:
        msg = "portal on"
        payload = msg.encode()
        ser.flush()
        ser.write(payload)
    

    if state is False:
        msg = "portal off"
        payload = msg.encode()
        ser.flush()
        ser.write(payload)
    return ''

@app.callback(
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
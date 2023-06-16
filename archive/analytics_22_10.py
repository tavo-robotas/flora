import os
import json
import time
import uuid
import dash
import pandas as pd
from PIL import Image
from os import listdir, getcwd
from os.path import isfile, join

import plotly.express as px
import dash_bootstrap_components as dbc
import utils.dash_reusable_components as drc
from utils.database_handle import DataBaseClient
from dash import html, dcc, callback, Input, Output, State
from utils.image_preprocess import show_histogram
from utils.image_preprocess import STORAGE_PLACEHOLDER, IMAGE_STRING_PLACEHOLDER, GRAPH_PLACEHOLDER


def get_indexes():
    path = f'{getcwd()}/assets/img/camera_captures/'
    directories = [ x for x in listdir(path)]
    return sorted(directories)

def get_instances(v):
    path = f'{getcwd()}/assets/img/camera_captures/{v}'
    files = [f for f in listdir(path) if isfile(join(path, f))]
    return sorted(files)

def get_image(idx, file):
    path = f'{getcwd()}/assets/img/camera_captures/{idx}/{file}'
    img = Image.open(path).copy()
    return drc.b64_to_pil(img)
    # return [
    #     drc.InteractiveImagePIL(
    #         image_id='image-output',
    #         image=im_pil,
    #         display_mode='fixed'
    #     )]

dash.register_page(__name__, path='/analytics')
session_id = str(uuid.uuid4())

controls = dbc.Card(
    [   
        html.H3("Plant selector"),
        html.Div(
            [
                dbc.Label("plant:idx"),
                dcc.Dropdown(
                    id="plant-idx",
                    options= get_indexes(),
                    value="id_0",
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("image instance"),
                dcc.Dropdown(
                    id="image-instance",
                    options=[],
                    value=get_instances('id_0')[0],
                ),
            ]
        )
    ],
    body=True,
)

charts = dbc.Row(
      [     dbc.Col(controls, width=2, class_name='pt-5'),
            dbc.Col(dcc.Graph(id='image-output', figure=fig), width=6),
            dbc.Col(dcc.Graph(id='graph-histogram'), width=4)
      ]
)
   

layout = html.Div(
      children=[
            html.H1(children='Growth analytics and predictions'),
            charts
])

@callback(
      Output('graph-histogram', 'figure'),
      Input('image-output', 'figure')
)
def update_histogram():
    im_pil = drc.b64_to_pil(string=drc.pil_to_b64(img))
    return show_histogram(im_pil)

callback(Output("image-instance", "options"), [Input("plant-idx", "value")])(
    get_instances
)

callback(
    Output('image-output', 'figure'),
    [Input("plant-idx", "value"), Input("image-instance", "value")])(
    get_image
)


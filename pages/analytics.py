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


#from ml.model import detect, filter_boxes, detr, transform
#from ml.model import CLASSES, COLORS, DEVICE


def get_indexes():
    path = f'{getcwd()}/assets/img/camera_captures/'
    directories = [ x for x in listdir(path)]
    return sorted(directories)

def get_instances(v):
    path = f'{getcwd()}/assets/img/camera_captures/{v}'
    files = [f for f in listdir(path) if isfile(join(path, f))]
    return sorted(files)

def get_image(idx, file, detection:bool=False):
    path = f'{getcwd()}/assets/img/camera_captures/{idx}/{file}'
    try:
        img = Image.open(path)
    except:
        return drc.incorrect_source()
    fig = drc.pil_to_fig(img, showlegend=True)

    if detection:
        t0 = time.time()
        scores, boxes = detect(img, detr, transform, device=DEVICE)
        scores = scores.data.numpy()
        boxes = boxes.data.numpy()

        t1 = time.time()

        existing_classes = set()
        
        for i in range(boxes.shape[0]):
            class_id = scores[i].argmax()
            label = CLASSES[class_id]
            confidence = scores[i].max()
            x0, y0, x1, y1 = boxes[i]

            # only display legend when it's not in the existing classes
            showlegend = label not in existing_classes
            text = f"class={label}<br>confidence={confidence:.3f}"

            drc.add_bbox(
                fig, x0, y0, x1, y1,
                opacity=0.7, group=label, name=label, color=COLORS[class_id], 
                showlegend=showlegend, text=text,
            )

            existing_classes.add(label)

    return fig


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
      [     dbc.Col(controls, width=3, class_name='pt-5'),
            dbc.Col(dcc.Graph(id='interactive-image'), width=3),
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
      Input('interactive-image', 'figure')
)
def update_histogram(fig):
    enc_str = fig['layout']['images'][0]['source'].split(';base64,')[-1]
    im_pil = drc.b64_to_pil(string=enc_str)
    return show_histogram(im_pil)

callback(Output("image-instance", "options"), [Input("plant-idx", "value")])(
    get_instances
)

callback(
    Output('interactive-image', 'figure'),
    [Input("plant-idx", "value"), Input("image-instance", "value")])(
    get_image
)


import os
import json
import time
import uuid
import dash
import pandas as pd
from copy import deepcopy
import plotly.express as px
import dash_bootstrap_components as dbc
from utils.database_handle import DataBaseClient
import utils.dash_reusable_components as drc
from dash import html, dcc, callback, Input, Output, State
from utils.image_preprocess import show_histogram, generate_lasso_mask
from utils.image_preprocess import STORAGE_PLACEHOLDER, IMAGE_STRING_PLACEHOLDER, GRAPH_PLACEHOLDER
from PIL import Image

dash.register_page(__name__, path='/analytics')

dbclient   = DataBaseClient()
collection = dbclient.get_all_records()

df   = pd.DataFrame(list(collection.find()))
df   = df.iloc[:, 1:]
data = df.to_dict('records')
img = Image.open('assets/img/01.jpg').copy()
fig = px.imshow(img)

session_id = str(uuid.uuid4())

      # def binary_record(self, image):
      #       b64 = base64.b64encode(image)
      #       bi  = binary.Binary(b64)
      #       return bi


if datetime.now().minute == 7 and datetime.now().second == 00:
    print('doing frame image', flush=True)
    time  = datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')
    frame = camera_idx0.get_frame()
    b64 = base64.b64encode(frame)
    bi  = binary.Binary(b64)
    record = {
            "name" : f'{camera_idx0.get_index()}_{time}',
            "time" : time,
            "image": bi
        }
    result = db.collection.insert_one(record)
    print(f'image record {result.inserted_id} was inserted', flush=True)




graph = dcc.Graph(
            id="temperature_graph", 
            figure=px.scatter_3d(data, x='temperature', y='humidity', z='soilmoisture', color='temperature'))


image = dbc.Row(
      [
            dbc.Col(
                  dcc.Graph(id='interactive-image', figure=fig), width=6
            ),
            dbc.Col(
                   dcc.Graph(id='graph-histogram'),
                   width=6
            )
      ]
)
   


layout = html.Div(
      children=[
            html.Div(session_id, id='session-id', style={'display': 'none'}),
            html.H1(children='Growth analytics and predictions'),
            image

])


@callback(
      Output('graph-histogram', 'figure'),
      [Input('interactive-image', 'figure')]
)
def update_histogram(figure):
    # Retrieve the image stored inside the figure
    
    #enc_str = figure['layout']['images'][0]['source'].split(';base64,')[-1]
    # Creates the PIL Image object from the b64 png encoding
    im_pil = drc.b64_to_pil(string=drc.pil_to_b64(img))

    return show_histogram(im_pil)
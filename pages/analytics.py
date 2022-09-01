import dash
import pandas as pd
from dash import html, dcc
import plotly.express as px
import dash_bootstrap_components as dbc
from utils.database_handle import DataBaseClient

dash.register_page(__name__)

dbclient   = DataBaseClient()
collection = dbclient.get_all_records()

df   = pd.DataFrame(list(collection.find()))
df   = df.iloc[:, 1:]
data = df.to_dict('records')

graph = dcc.Graph(
            id="temperature_graph", 
            figure=px.scatter_3d(data, x='temperature', y='humidity', z='soilmoisture', color='temperature'))

layout = html.Div(
      children=[
            html.H1(children='Data analytics and predictions'),
            html.Div(children=''),
            graph
])
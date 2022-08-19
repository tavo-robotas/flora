import dash
from dash import html, dcc

dash.register_page(__name__)

layout = html.Div(
      children=[
            html.H1(children='This is our ML analytics page'),
            html.Div(children='Here we will have very cool AI algorithms doing horticulture data analysis')
])
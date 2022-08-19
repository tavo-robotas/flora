
from dash import html, dcc, callback, Input, Output
from utils.database_handle import DataBaseClient
import dash_bootstrap_components as dbc
import pandas as pd
import dash

dbclient   = DataBaseClient()
collection = dbclient.get_all_records()

df    = pd.DataFrame(list(collection.find())).iloc[:, 1:]
table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, index=True, responsive=True )
pagination = dbc.Pagination(id="pagination", first_last=True, previous_next=True, max_value=10)
dash.register_page(__name__)

layout = html.Div(children=[
      pagination,
      table
])



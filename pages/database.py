
from dash import html, dcc, callback, Input, Output
from utils.database_handle import DataBaseClient
import dash_bootstrap_components as dbc
import pandas as pd
import dash

dash.register_page(__name__, path='/database')

dbclient   = DataBaseClient()
collection = dbclient.get_all_records()
df         = pd.DataFrame(list(collection.find())).iloc[:, 1:]

pagination = dbc.Row(
      [
            dbc.Col(
                  html.Div(
                        dbc.Pagination(id="pagination", first_last=True, previous_next=True, max_value=10)
                       
                  )
            ),
            dbc.Col(
                  html.Div(
                        [
                              dbc.Button("download data", outline=True, id="btn-download-data", color="primary", className="me-1"),
                              dcc.Download(id="download-data")
                        ]
                  )
            )
      ]
)

table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, index=True, responsive=True )
dash.register_page(__name__)

layout = html.Div(children=[
      pagination,
      table
])

@callback(
      Output("download-data", "data"),
      Input("btn-download-data", "n_clicks"),
      prevent_initial_call=True,
)
def func(n_clicks):
      cols = df.columns
      return dcc.send_data_frame(df.to_csv, "flora_data.csv")




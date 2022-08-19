from utils.camera_stream  import VideoCamera, gen 
import dash_bootstrap_components as dbc
from flask import Flask, Response
from dash import Dash, html, dcc
import dash

server = Flask(__name__)

app = dash.Dash(
    __name__, 
    server=server,
    url_base_pathname='/',
    use_pages=True,
    title='flora',
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

def Header(name, app):
    title = html.H2(name, style={"marginTop": 5})
    parag = html.P('Process managment and reporting')
    logo = html.Img(
        src=app.get_asset_url("flora-logo.png"), style={"height": 80}
    )
    return dbc.Row([dbc.Col([title,parag], class_name='p-2', md=12)])

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
        "backgroundColor": "#f8f9fa"
    }
)

app.layout = dbc.Container(
    [ 
      sidebar,
      Header("Horticulture monitoring dashboard", app),   
	dash.page_container
    ],
    fluid=True,
    style={
        "marginLeft": "12rem",
        "marginRight": "2rem",
        "padding": "2rem 1rem"

    },
    id="page-content",
    class_name="w-auto"
)


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

if __name__ == '__main__':
	app.run_server(debug=True,port=8080,host='0.0.0.0')
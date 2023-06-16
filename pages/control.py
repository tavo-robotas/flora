from dash import html, dcc, callback, Input, Output
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from utils.serializer import serialPort 
import plotly.graph_objects as go
import dash_daq as daq
import dash

ser = serialPort(port='/dev/ttyUSB0', baudrate=9600)
cnc = serialPort(port='/dev/ttyUSB1', baudrate=115200)

dash.register_page(__name__, path='/control')

tabs  = dbc.Tabs(
    [
        dbc.Tab(label="vision",     tab_id="camera_feed"),
        dbc.Tab(label="control",    tab_id="control_panel")
    ],
    id="data_tabs",
    active_tab="control_panel",
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
            html.H4("camera idx:0", className="display-6 fw-bold"),
            html.Hr(className="my-2"),
            html.Img(src="/video_feed/0", className="mh-100 w-100 h-auto"),
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
            html.H4("camera idx:1", className="display-6 fw-bold"),
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
            html.H4("camera idx:2", className="display-6 fw-bold"),
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

layout = html.Div(children=[
            dbc.Row(dbc.Col(tabs)),
            html.Div(id="tab-content"),
            html.H1("XY Control"),
            html.Button('Unlock', id='unlock-button', n_clicks=0),
                  html.Div(
                  children=[
                  html.H2("X-Axis"),
                  html.Button('Move Left', id='move-left-x-button', n_clicks=0),
                  html.Button('Move Right', id='move-right-x-button', n_clicks=0),
                  html.Div(
                        children=[
                              html.Label('Feed Rate'),
                              dcc.Input(id='x-feed-input', type='number', value=100),
                        ],
                        style={'margin-top': '10px'}
                  ),
                  html.Div(
                        children=[
                              html.Label('Step Size'),
                              dcc.Input(id='x-step-input', type='number', value=0.1),
                        ],
                        style={'margin-top': '10px'}
                  ),
                  ],
                  className="axis-control"
            ),
            html.Div(
                  children=[
                  html.H2("Y-Axis"),
                  html.Button('Move Up', id='move-up-y-button', n_clicks=0),
                  html.Button('Move Down', id='move-down-y-button', n_clicks=0),
                  html.Div(
                        children=[
                              html.Label('Feed Rate'),
                              dcc.Input(id='y-feed-input', type='number', value=100),
                        ],
                        style={'margin-top': '10px'}
                  ),
                  html.Div(
                        children=[
                              html.Label('Step Size'),
                              dcc.Input(id='y-step-input', type='number', value=0.1),
                        ],
                        style={'margin-top': '10px'}
                  ),
                  ],
                  className="axis-control"
            ),
            html.Div(
                  children=[
                  dcc.Graph(
                        id='cnc-grid',
                        figure=go.Figure(
                              data=[],
                              layout=go.Layout(
                              width=600,
                              height=600,
                              xaxis=dict(
                                    range=[0, 10],
                                    showgrid=True,
                                    dtick=1
                              ),
                              yaxis=dict(
                                    range=[0, 10],
                                    showgrid=True,
                                    dtick=1
                              ),
                              margin=dict(l=40, r=40, t=40, b=40)
                              )
                        ),
                        config={'editable': False, 'displayModeBar': False}
                  )
                  ],
                  style={'display': 'flex', 'justify-content': 'center'}
            ),
            html.Div(
                  children=[
                  html.H2("Current Position:"),
                  html.P(id='current-position')
                  ],
                  style={'text-align': 'center', 'margin-top': '20px'}
            ),
            html.Div(
                  children=[
                  html.H2("Move to Position:"),
                  dcc.Input(id='x-coordinate', type='number', placeholder='X-coordinate', min=0, max=10),
                  dcc.Input(id='y-coordinate', type='number', placeholder='Y-coordinate', min=0, max=10),
                  html.Div(
                        children=[
                              html.Label('Feed Rate'),
                              dcc.Input(id='feed-rate-input', type='number', placeholder='Feed Rate', min=0)
                        ],
                        style={'margin-top': '10px'}
                  ),
                  html.Div(
                        children=[
                              html.Label('Step Size'),
                              dcc.Input(id='step-size-input', type='number', placeholder='Step Size', min=0)
                        ],
                        style={'margin-top': '10px'}
                  ),
                  html.Button('Move', id='move-button', n_clicks=0)
                  ],
                  style={'text-align': 'center', 'margin-top': '20px'}
            )
])

def cmd_rcv(state, msg):
    print(f'state: {state}')
    print(f'msg:   {msg}')
    payload = msg.encode()
    ser.flush()
    ser.writer(payload)
    val = ser.reader()  
    print(f'val: {val}')
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
        if active_tab == "camera_feed":
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

@callback(
    Output('unlock-button', 'children'),
    [Input('unlock-button', 'n_clicks')]
)
def unlock_controller(n_clicks):
    if n_clicks > 0:
        try:
            # Send unlock command to GRBL controller
            command = '$X\n'
            cnc.writer(command.encode())
            return 'Unlock'  # Reset the button label
        except serial.SerialException as e:
            print(f"Error: Serial communication failed. {str(e)}")
            return 'Unlock'
    else:
        return 'Unlock'

@callback(
    Output('cnc-grid', 'figure'),
    [Input('cnc-grid', 'clickData')],
    [State('feed-rate-input', 'value'), State('step-size-input', 'value')]
)
def update_grid(click_data, feed_rate, step_size):
    # Handle click events on the grid
    if click_data:
        try:
            x = click_data['points'][0]['x']
            y = click_data['points'][0]['y']
            # Send GRBL command to move the gantry to the clicked location with feed rate and step size
            command = f'G1 X{x} Y{y} F{feed_rate} S{step_size}\n'
            ser.write(command.encode())
        except serial.SerialException as e:
            print(f"Error: Serial communication failed. {str(e)}")
    return go.Figure(
        data=[],
        layout=go.Layout(
            width=600,
            height=600,
            xaxis=dict(
                range=[0, 10],
                showgrid=True,
                dtick=1
            ),
            yaxis=dict(
                range=[0, 10],
                showgrid=True,
                dtick=1
            ),
            margin=dict(l=40, r=40, t=40, b=40)
        )
    )



@callback(
    Output('current-position', 'children'),
    [Input('cnc-grid', 'clickData')]
)
def update_current_position(click_data):
    # Update the current position display
    if click_data:
        x = click_data['points'][0]['x']
        y = click_data['points'][0]['y']
        return f'X: {x}, Y: {y}'
    else:
        return 'X: N/A, Y: N/A'


@callback(
    Output('move-left-x-button', 'children'),
    [Input('move-left-x-button', 'n_clicks')],
    [dash.dependencies.State('x-feed-input', 'value'), dash.dependencies.State('x-step-input', 'value')]
)
def move_left_x_axis(n_clicks, feed, step):
    if n_clicks > 0:
        try:
            # Send GRBL command to move the X-axis left
            command = f'G1 X-{step} F{feed}\n'
            cnc.writer(command.encode())
            return 'Move Left'  # Reset the button label
        except serial.SerialException as e:
            print(f"Error: Serial communication failed. {str(e)}")
            return 'Move Left'
    else:
        return 'Move Left'

@callback(
    Output('move-right-x-button', 'children'),
    [Input('move-right-x-button', 'n_clicks')],
    [dash.dependencies.State('x-feed-input', 'value'), dash.dependencies.State('x-step-input', 'value')]
)
def move_right_x_axis(n_clicks, feed, step):
    if n_clicks > 0:
        try:
            # Send GRBL command to move the X-axis right
            command = f'G1 X{step} F{feed}\n'
            cnc.writer(command.encode())
            return 'Move Right'  # Reset the button label
        except serial.SerialException as e:
            print(f"Error: Serial communication failed. {str(e)}")
            return 'Move Right'
    else:
        return 'Move Right'

@callback(
    Output('move-up-y-button', 'children'),
    [Input('move-up-y-button', 'n_clicks')],
    [dash.dependencies.State('y-feed-input', 'value'), dash.dependencies.State('y-step-input', 'value')]
)
def move_up_y_axis(n_clicks, feed, step):
    if n_clicks > 0:
        try:
            # Send GRBL command to move the Y-axis up
            command = f'G1 Y{step} F{feed}\n'
            cnc.writer(command.encode())
            return 'Move Up'  # Reset the button label
        except serial.SerialException as e:
            print(f"Error: Serial communication failed. {str(e)}")
            return 'Move Up'
    else:
        return 'Move Up'

@callback(
    Output('move-down-y-button', 'children'),
    [Input('move-down-y-button', 'n_clicks')],
    [dash.dependencies.State('y-feed-input', 'value'), dash.dependencies.State('y-step-input', 'value')]
)
def move_down_y_axis(n_clicks, feed, step):
        if n_clicks > 0:
            try:
                # Send GRBL command to move the Y-axis down
                command = f'G1 Y-{step} F{feed}\n'
                cnc.writer(command.encode())
                return 'Move Down'  # Reset the button label
            except serial.SerialException as e:
                print(f"Error: Serial communication failed. {str(e)}")
                return 'Move Down'
        else:
            return 'Move Down'


from dash import dcc
from dash import html
import json
import plotly.graph_objs as go
import utils.dash_reusable_components as drc
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance

# [filename, image_signature, action_stack]
STORAGE_PLACEHOLDER = json.dumps({
    'filename': None,
    'image_signature': None, 
    'action_stack': []
})
IMAGE_STRING_PLACEHOLDER = drc.pil_to_b64(Image.open('assets/img/samples/01.jpg').copy(), enc_format='jpeg')
GRAPH_PLACEHOLDER = dcc.Graph(id='interactive-image', style={'height': '80vh'})




def show_histogram(image):
    def hg_trace(name, color, hg):
        line = go.Scatter(
            x=list(range(0, 256)),
            y=hg,
            name=name,
            line=dict(color=(color)),
            mode='lines',
            showlegend=False
        )
        fill = go.Scatter(
            x=list(range(0, 256)),
            y=hg,
            name=name,
            line=dict(color=(color)),
            fill='tozeroy',
            hoverinfo='none'
        )

        return line, fill

    hg = image.histogram()

    if image.mode == 'RGBA':
        rhg = hg[0:256]
        ghg = hg[256:512]
        bhg = hg[512:768]
        ahg = hg[768:]

        data = [
            *hg_trace('Red', '#FF4136', rhg),
            *hg_trace('Green', '#2ECC40', ghg),
            *hg_trace('Blue', '#0074D9', bhg),
            *hg_trace('Alpha', 'gray', ahg)
        ]

    elif image.mode == 'RGB':
        # Returns a 768 member array with counts of R, G, B values
        rhg = hg[0:256]
        ghg = hg[256:512]
        bhg = hg[512:768]

        data = [
            *hg_trace('Green', '#2ECC40', ghg),
        ]

    else:
        data = [*hg_trace('Gray', 'gray', hg)]
       
    layout = go.Layout(
        legend=dict(x=0, y=1.15, orientation="h")
    ).update(showlegend=False)

    return go.Figure(data=data, layout=layout)
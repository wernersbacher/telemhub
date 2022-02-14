import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json


def create_telem_plot(df):
    trace1 = {
        "x": df["dist_lap"],
        "y": df["speedkmh"],
        "mode": "lines",
        "name": 'value',
        "type": 'scatter',
    }

    layout = {

        'yaxis': {
            'title': "Speed (km/h)",
        },

        'xaxis': {
            'title': "Distance (m)",
        },

    }

    data = [trace1]
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(title_text='Speed vs. Distance')

    figure_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return figure_json

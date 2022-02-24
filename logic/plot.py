import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json


def create_telem_plot(df, df2):
    """ Todo: add 2nd trace with legend"""

    trace1 = {
        "x": df["dist_lap"],
        "y": df["speedkmh"],
        "mode": "lines",
        "name": 'Speed',
        "type": 'scatter',
        "line": {"color": 'blue'}
    }
    trace2 = {
        "x": df["dist_lap"],
        "y": df["throttle"],
        "mode": "lines",
        "name": 'Throttle',
        "type": 'scatter',
        "line": {"color": 'green'}
    }
    trace3 = {
        "x": df["dist_lap"],
        "y": df["brake"],
        "mode": "lines",
        "name": 'Brake',
        "type": 'scatter',
        "line": {"color": 'red'}
    }

    # subplot setup
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01)

    fig.append_trace(trace1, row=1, col=1)
    fig.append_trace(trace2, row=2, col=1)
    fig.append_trace(trace3, row=3, col=1)
    fig['layout']['xaxis3']['title'] = 'Distance (meters)'

    figure_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return figure_json

"""This module contains helper functions for making visualisations
"""
from typing import Dict, Any
import pandas as pd

def plot_dataframe(dataframe: pd.DataFrame, max_y_axis: int = None) -> Dict[str, Any]:
    """Returns dictionary used for plotly graphs
    Arguments:
        dataframe: The dataframe to plot. Plots all columns as y, index is x.
        max_y_axis: Maximal value on y-axis.
    """

    if max_y_axis is None:
        yaxis = {}
    else:
        yaxis = {"range": (0, max_y_axis), "autorange": False}

    return {'data': [
        {
            "x": dataframe.index,
            "y": dataframe[col].astype(int),
            "name": col,
            "mode": "lines",
        }
        for col in dataframe.columns
    ], 'layout': {
        "yaxis": yaxis,
        "xaxis": {"rangeslider": {
            "visible": True
        }},
        "yaxis_title": "Number of people",
        "title": "Covid 19 projection",
        "legend": {"orientation": "h", "y": 1, "x": 0},
        "font": {
            "family": "Roboto",
            "size": 14,
            "color": "#1372B3"
        },
        "hovermode": "x"
    }}

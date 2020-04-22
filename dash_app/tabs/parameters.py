"""This contains the layout for the parameters tabs
"""
import dash_html_components as html
from dash_app.utils.utils import generate_table
from dash_app.utils.utils import create_dataframe_from_parameters


tab_1_layout = html.Div([
    html.H1('Parameters'),
    generate_table(create_dataframe_from_parameters(), max_rows=30)
])

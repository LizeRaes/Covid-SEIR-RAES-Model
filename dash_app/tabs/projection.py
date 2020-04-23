"""this file contains the layout for the projection tab
"""
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import dash_table
from dash_app.utils.utils import generate_table
from dash_app.utils.utils import create_dataframe_from_parameters

params = [
    'Event', 'Date', 'R0'
]
example_measures = pd.read_excel(
    "dash_app/data/measures_test.xlsx", sheet_name='R0')

example_measures['Date'] = pd.to_datetime(example_measures['Date']).dt.date

df_parameters = create_dataframe_from_parameters()

facts = dcc.Dropdown(
    id='facts',
    options=[
        {'label': 'Confirmed', 'value': 'confirmed'},
        {'label': 'Hospitalized', 'value': 'hospital'},
        {'label': 'Intensive Care', 'value': 'ICU'},
        {'label': 'Deaths', 'value': 'death'}
    ],
    value=['hospital'],
    multi=True
)

# the style arguments for the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": '119px',
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#4E4E4E",
    "overflow-y": "scroll",
    "overflow-x": "scroll"
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "22rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H5("Scenario generator", style={'margin-bottom': "20px"}),
        dash_table.DataTable(
            id='measure_input',
            columns=(
                [{'id': p, 'name': p} for p in params]
            ),
            data=example_measures.to_dict('records'),
            editable=True,
            row_deletable=True
        ),
        html.Button('+ Add measure', id='editing-rows-button', n_clicks=0),
        html.Hr(),
        html.Button(
            "Toggle Expert parameters",
            id="collapse-button"
        ),
        html.Br(),
        html.Br(),
        dbc.Collapse(
            dash_table.DataTable(
                id='parameters_input',
                columns=(
                    [{'id': p, 'name': p} for p in df_parameters.columns]
                ),
                data=create_dataframe_from_parameters().to_dict('records'),
                editable=False,
        ),
            id="collapse")
    ],
    style=SIDEBAR_STYLE
)

content = html.Div(
    [
        facts,
        html.Div(
            children=[
                dcc.Graph(
                    id='projection-chart'
                ),
                dcc.Graph(
                    id='expert-chart'
                )]
        )
    ],
    id="page-content",
    style=CONTENT_STYLE)


tab_layout = html.Div([
    sidebar, content
])
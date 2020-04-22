"""This file contains the dash app
"""
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd

from dash.dependencies import Input, Output, State
from dash_app.tabs import current
from dash_app.tabs import parameters
from dash_app.tabs import projection
from dash_app.utils.plotting import plot_dataframe

from raes_seir.model.parameters import Parameters
from raes_seir.model.measures import Measures
from raes_seir.model.model import Model




TEST_PARAM = Parameters()

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Covid-19 Dashboard"),
                    html.H6("Projection Reporting"),
                ],
            )
        ],
    )


# Build tabs
def build_tabs_not_used():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab-1",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Parameter-tab",
                        label="Parameters Used",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Current-tab",
                        label="Current situation",
                        value="tab-2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Projection-tab",
                        label="Projection",
                        value="tab-3",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    )
                ],
            )
        ],
    )


# Create HTML structure

# Import stylesheets
EXTERNAL_STYLESHEETS = [
    'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=EXTERNAL_STYLESHEETS,
    assets_folder='dash_app/assets'
)
app.title = 'Covid-19 Dashboard'
server = app.server

app.config['suppress_callback_exceptions'] = True

app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        dcc.Tabs(id="tabs", value='tab-1-example', children=[
            dcc.Tab(
                id="Parameter-tab",
                label="Parameters",
                value="tab-1",
                className="custom-tab",
                selected_className="custom-tab--selected",
            ),
            dcc.Tab(
                id="Current-tab",
                label="Current situation",
                value="tab-2",
                className="custom-tab",
                selected_className="custom-tab--selected",
            ),
            dcc.Tab(
                id="Projection-tab",
                label="Projection",
                value="tab-3",
                className="custom-tab",
                selected_className="custom-tab--selected",
            ),
        ]),
        html.Div(id='tabs-content')
    ],
)


# CALLBACKS
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return parameters.tab_1_layout
    elif tab == 'tab-2':
        return current.tab_2_layout
    elif tab == 'tab-3':
        return projection.tab_3_layout

@app.callback(
    Output('measure_input', 'data'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('measure_input', 'data'),
     State('measure_input', 'columns')])
def add_row(n_clicks, rows, columns):
    """this function will add an extra row in the datable
    Args:
        n_clicks: number of clicks
        rows: list of values in datatable
        columns: list of datatable column names

    Returns:
        list of rows with a new one appended
    """
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback(
    Output(component_id='projection-chart', component_property='figure'),
    [Input(component_id='measure_input', component_property='data'),
     Input(component_id='measure_input', component_property='columns')]
)
def plot_projection(rows, columns):
    """this function makes a visualisation with the applied measures.
    Args:
        rows: data in the datatable
        columns: list of datatable columnn names

    Returns:
        graph of the raes_seir simulation model
    """
    input_measures = pd.DataFrame(
        rows, columns=[c['name'] for c in columns]).to_dict('list')
    test_measure = Measures.fromList(
        input_measures['Date'], input_measures['R0'])
    test_output = Model.generate_projection({}, TEST_PARAM, test_measure)
    temp = plot_dataframe(test_output)
    return temp


if __name__ == '__main__':
    app.run_server(port=int(os.environ.get('PORT', 8080)), debug=True)

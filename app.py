"""This file contains the dash app
"""
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

from dash.dependencies import Input, Output, State
from dash_app.tabs import current
from dash_app.tabs import parameters
from dash_app.tabs import projection
from dash_app.utils.plotting import plot_dataframe
from dash_app.tabs.current import pv_hosp
from dash_app.tabs.current import df_sex
from dash_app.tabs.current import pv_mort

from raes_seir.model.parameters import Parameters
from raes_seir.model.measures import Measures
from raes_seir.model.model import Model

TEST_PARAM = Parameters()


def build_banner():
    """Generate the banner
    """
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    dbc.Row([
                        dbc.Col(
                            html.Div([
                                html.Img(id="logo", src=APP.get_asset_url("virus_white.svg"), style={'display': 'inline-block'}),
                                html.H5("Covid-19 Dashboard", style={'display': 'inline-block'})])
                        ),
                        dbc.Col(
                            html.A([
                                html.Img(id="git_img", src=APP.get_asset_url("git.png"))
                            ], href='https://github.com/LizeRaes/Covid-SEIR-RAES-Model', target="_blank", style={'float': 'right', 'margin-right': '20px'})
                        )
                    ])
                    ,
                ])
        ]
    )

# Create HTML structure


# Import stylesheets
EXTERNAL_STYLESHEETS = [
    'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']

APP = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=EXTERNAL_STYLESHEETS,
    assets_folder='dash_app/assets'
)
APP.title = 'Covid-19 Dashboard'
SERVER = APP.server

APP.config['suppress_callback_exceptions'] = True

APP.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        dcc.Tabs(id="tabs", className='control-tabs', children=[
            dcc.Tab(
                id="Current-tab",
                label="Current situation",
                value="tab-1",
                className="custom-tab",
                selected_className="custom-tab--selected",
            ),
            dcc.Tab(
                id="Parameter-tab",
                label="Parameters",
                value="tab-2",
                className="custom-tab",
                selected_className="custom-tab--selected"
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
@APP.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    """This function wil return the specified tab

    Args:
        tab (str): tab name

    Returns:
        layout tab
    """
    if tab == 'tab-1':
        return current.tab_layout
    elif tab == 'tab-2':
        return parameters.tab_layout
    elif tab == 'tab-3':
        return projection.tab_layout


@APP.callback(
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


@APP.callback(
    Output(component_id='projection-chart', component_property='figure'),
    [
        Input('facts', 'value'),
        Input(component_id='measure_input', component_property='data'),
        Input(component_id='measure_input', component_property='columns')
    ]
)
def plot_projection(facts, rows, columns):
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
    pv_sex = df_sex.groupby(['DATE'], as_index=False).sum()
    fig = go.Figure()
    # Add traces
    for element in temp['data']:
        if element["name"] in ['confirmed_today', 'hospital_today',
                               'ICU_today', 'confirmed_today', 'deaths_today']:
            element["name"] = 'Predicted_' + element["name"]
            element["line"] = dict(width=4, dash='dot')
            fig.add_trace(element)
    fig.add_trace(go.Scatter(x=pv_hosp["DATE"], y=pv_hosp["TOTAL_IN"],
                             mode='lines',
                             name='Actual_hospitalized')
                  )
    fig.add_trace(go.Scatter(x=pv_hosp["DATE"], y=pv_sex["CASES"],
                             mode='lines',
                             name='Actual_confirmed')
                  )
    fig.add_trace(go.Scatter(x=pv_mort["DATE"], y=pv_mort["DEATHS"],
                             mode='lines',
                             name='Actual_deaths',
                             ))
    updated_fig = go.Figure()
    for fact in facts:
        for element in fig['data']:
            if fact in element['name']:
                updated_fig.add_trace(element)
    updated_fig.update_layout(temp['layout'])
    return updated_fig


if __name__ == '__main__':
    APP.run_server(port=int(os.environ.get('PORT', 8080)), debug=True)

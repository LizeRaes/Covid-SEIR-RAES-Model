import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import *

# Create a parameter table that can be updated
df_params = pd.read_csv("./data/parameters.csv", sep=';')
params = list(df_params)


# FUNCTIONS
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


tab_1_layout = html.Div([
    html.H1('Parameters'),
    # Manually select metrics

    generate_table(df_params)

])

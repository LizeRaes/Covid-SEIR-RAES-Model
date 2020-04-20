import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
from raes_seir.model.parameters import Parameters 

# Create a parameter table that can be updated
df_params = pd.read_csv("dash_app/data/parameters.csv", sep=';')
params = list(df_params)

def create_dataframe_from_parameters():
    input_parameters = Parameters()
    print(input_parameters)
    list_dict = []
    for key,value in vars(input_parameters).items():
        temp_dict = {}
        temp_dict['Description'] = key
        temp_dict['Value'] = value
        list_dict.append(temp_dict)

    # parameter_table = dash_table.DataTable(
    #     id='table',
    #     columns=[
    #     {'name': 'Description', 'id': 'Description'},
    #     {'name': 'Value', 'id': 'Value'}],
    #     data=pd.DataFrame(list_dict).to_dict('records')
    # )
    return pd.DataFrame(list_dict)

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
    #generate_dash_table(),
    generate_table(create_dataframe_from_parameters())
])

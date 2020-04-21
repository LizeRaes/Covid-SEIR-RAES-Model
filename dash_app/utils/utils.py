"""this module contains general helper functions
"""
import pandas as pd
import dash_html_components as html

from raes_seir.model.parameters import Parameters


def create_dataframe_from_parameters():
    """this functions return the model parameters

    Returns:
        DataFrame object with description and value of parameters
    """
    input_parameters = Parameters()
    print(input_parameters)
    list_dict = []
    for key, value in vars(input_parameters).items():
        temp_dict = {}
        temp_dict['Description'] = key
        temp_dict['Value'] = value
        list_dict.append(temp_dict)

    return pd.DataFrame(list_dict)

# FUNCTIONS


def generate_table(dataframe, max_rows=10):
    """this function generates an html table fomr a dataframe

    Args:
        dataframe: a pandas DataFrame
        max_rows (int, optional): number of rows in table Defaults to 10.

    Returns:
        html table
    """
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

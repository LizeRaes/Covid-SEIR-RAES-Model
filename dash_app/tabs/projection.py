"""this file contains the layout for the projection tab
"""
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_table

params = [
    'Date', 'R0'
]
example_measures = pd.read_excel(
    "dash_app/data/param_test.xlsx", sheet_name='R0')

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


tab_layout = html.Div([
    # Left filter pane
    html.Div(
        [
            facts,
            dash_table.DataTable(
                id='measure_input',
                columns=(
                    [{'id': p, 'name': p} for p in params]
                ),
                data=example_measures.to_dict('records'),
                editable=True,
                row_deletable=True,
                style_cell={
                    'height': 'auto',
                    'minWidth': '0px', 'maxWidth': '2px',
                    'whiteSpace': 'normal'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            ),
            html.Button('Add a measure', id='editing-rows-button', n_clicks=0),

            # dcc.DatePickerRange(
            #     id='my-date-picker-range',
            #     start_date_placeholder_text="Start Period",
            #     end_date_placeholder_text="End Period",
            #     calendar_orientation='vertical',
            #     start_date=datetime.date(2020, 3, 1),
            #     end_date=datetime.datetime.today()
            # )
        ]
    ),
    html.Div([
        html.Div(children=[
            dcc.Graph(
                id='projection-chart'
            )]
            )
    ])
])

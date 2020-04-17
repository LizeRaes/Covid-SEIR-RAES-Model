import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import datetime
import pandas as pd
import numpy as np
from itertools import tee, islice, chain

#local import
from classes import parameters
from classes import actual
from classes import measures
from classes import model

# VARIABLES
confirmed_cases_hosp = 0.49  # C7
avg_hosp_stay = 12  # C8
delay_test = 1  # C9
total_population = 11400000  # C10
avg_delay_infection_case = 12  # C18
avg_contagious_period = 4  # C19

df_proj_view = 0


# FUNCTIONS
def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)


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


# import CSV
df_sex = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_CASES_AGESEX.csv', sep=',', encoding='latin-1')
df_hosp = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_HOSP.csv', sep=',', encoding='latin-1')

# Pivot
pv_sex = df_sex.groupby(['DATE'], as_index=False).sum()

# create new dataframe
start_date_v = datetime.date(2020, 3, 1)
end_date_v = datetime.date(2020, 12, 1)
days = pd.date_range(start_date_v, end_date_v)
df_proj = pd.DataFrame({'DATE': days})

# Confirmed cases (today)
pv_sex["DATE"] = pv_sex["DATE"].astype('datetime64[ns]')
df_proj = pd.merge(df_proj, pv_sex, on='DATE', how='left')

# Cumulative confirmed cases
df_proj["CUMUL CASES"] = df_proj["CASES"].cumsum()

# Measures
measures = {'DATE': [datetime.date(2020, 2, 1), datetime.date(2020, 3, 10), datetime.date(2020, 3, 12),
                     datetime.date(2020, 3, 13), datetime.date(2020, 3, 18), datetime.date(2020, 12, 1)],
            'R0': [2.640, 1.320, 1.380, 1.278, 0.980, 0]}
df_measures = pd.DataFrame(measures)
df_measures["DATE"] = df_measures["DATE"].astype('datetime64[ns]')

# Calculations for projection
# Growth factor(iterate over the measures list)
df_proj["Growth Factor"] = 0

for i in range(len(df_proj['DATE']) - 1):
    for x in range(len(df_measures["DATE"]) - 1):
        if (df_proj['DATE'].iloc[i] >= df_measures['DATE'].iloc[x]) & (
                df_proj['DATE'].iloc[i] < df_measures['DATE'].iloc[x + 1]):
            df_proj["Growth Factor"].iloc[i] = df_measures["R0"].iloc[x] / avg_contagious_period

growth_factor_decrease = 0  # TODO


# Real infected today


# Contagious today

# Transmission rate


pv_hosp = df_hosp.groupby(['DATE'], as_index=False).sum()
df_proj_view = df_proj

# Create figures for charts

fig_hosp = go.Figure()
fig_hosp.add_trace(go.Scatter(x=df_proj["DATE"], y=df_proj["CASES"],
                              mode='lines',
                              name='Total in'))

tab_3_layout = html.Div([
    # Left filter pane
    html.Div(
        [
            dcc.DatePickerRange(
                id='my-date-picker-range',
                start_date_placeholder_text="Start Period",
                end_date_placeholder_text="End Period",
                calendar_orientation='vertical',
                start_date=datetime.date(2020, 3, 1),
                end_date=datetime.datetime.today()
            )],
        className="pretty_container"
    ),
    html.Div([
        html.Div(children=[
            dcc.Graph(
                id='projection-chart',
                figure=fig_hosp
                # layout=
            )],
            # className="three columns tile"
        )]),
    generate_table(df_proj_view, 1000),

    html.Div(id='page-3-content')

])
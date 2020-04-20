import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
#from app import *
import numpy as np
import plotly.express as px
from urllib.request import urlopen
import json
import pandas as pd

# TODO add labels for hosp, resp, deaths,...
# TODO add date slider

# with urlopen('https://github.com/arneh61/Belgium-Map/blob/master/Provincies.json') as response:
#    provinces = json.load(response)

pwc_colors = {"#D04A02", "#EB8C00", "#FFB600", "#DB536A", "#E0301E", "#7D7D7D", "#DEDEDE"}

# Load CSV files from https://epistat.sciensano.be
df_sex = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_CASES_AGESEX.csv', sep=',', encoding='latin-1')
# df_muni = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_CASES_MUNI.csv', sep=',', encoding='latin-1')
df_muni_cum = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_CASES_MUNI_CUM.csv', sep=',', encoding='latin-1')
df_hosp = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_HOSP.csv', sep=',', encoding='latin-1')
df_mort = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_MORT.csv', sep=',', encoding='latin-1')
df_tests = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_tests.csv', sep=',', encoding='latin-1')

# PIVOTS
pv_sex = pd.pivot_table(df_sex, values='CASES', columns=['SEX'], aggfunc=np.sum)
pv_hosp = df_hosp.groupby(['DATE'], as_index=False).sum()
pv_mort = df_mort.groupby(['DATE'], as_index=False).sum()
pv_mort_age = df_mort.groupby(['AGEGROUP'], as_index=False).sum()

# pd.pivot_table(df_hosp, values='')

# replacing na values in df_sex
df_sex["SEX"].fillna("No info", inplace=True)

layout = go.Layout(
    autosize=True,
    margin=dict(l=0, r=0, b=0, t=4, pad=8),
    paper_bgcolor="white",
    plot_bgcolor="white",
)

# Modify df_muni_cum
# split column TX_PROV_DESCR_NL
df_muni_cum[["NaN", "Provinces"]] = df_muni_cum["TX_PROV_DESCR_NL"].str.split(" ", expand=True, )

# split_data = df_muni_cum["TX_PROV_DESCR_NL"].str.split(" ")
# data = split_data.to_list()
#
# df_muni_cum = pd.DataFrame(df_muni_cum, columns=names)

# replace <5 values to 3 (so that we can make calculations)
df_muni_cum.replace('<5', 3, inplace=True)
df_muni_cum["CASES"] = pd.to_numeric(df_muni_cum["CASES"])
df_muni_cum["Provinces"] = df_muni_cum["Provinces"].astype(str)

# replace

# Create map chart
with open("dash_app/assets/muni.json") as response:
    municipalities = json.load(response)

#print(municipalities["features"][0])

fig_map = px.choropleth_mapbox(df_muni_cum, geojson=municipalities, locations='TX_DESCR_NL', color='CASES',
                               color_continuous_scale="Oranges",
                               #                           range_color=(0, 12),
                               mapbox_style="carto-positron",
                               zoom=6, center={"lat": 50.5039, "lon": 4.4699},
                               opacity=0.5,
                               labels={'CASES': 'Cases'}
                               )

lay_map = go.Layout(title='Heatmap', showlegend=False)

# Create pie chart
fig_pie = px.pie(df_sex, values='CASES', title="Cases by sex", names="SEX",
                 color_discrete_map={'M': "#D04A02",
                                     'F': "#EB8C00",
                                     'No info': "#DEDEDE"
                                     })

# Create line graph (hospitalisations)
fig_hosp = go.Figure()
fig_hosp.add_trace(go.Scatter(x=pv_hosp["DATE"], y=pv_hosp["TOTAL_IN"],
                              mode='lines',
                              name='Total in',
                              line=dict(color="#D04A02")
                              ))
fig_hosp.add_trace(go.Scatter(x=pv_hosp["DATE"], y=pv_hosp["TOTAL_IN_ICU"],
                              mode='lines',
                              name='Total in ICU',
                              line=dict(color="#EB8C00")
                              ))
fig_hosp.add_trace(go.Scatter(x=pv_hosp["DATE"], y=pv_hosp["TOTAL_IN_RESP"],
                              mode='lines',
                              name='Total in resp',
                              line=dict(color="#FFB600")
                              ))
fig_hosp.add_trace(go.Scatter(x=pv_hosp["DATE"], y=pv_hosp["TOTAL_IN_ECMO"],
                              mode='lines',
                              name='Total in_ECMO',
                              line=dict(color="#DB536A")
                              ))

# Create line graph (deaths)
fig_line_deaths = go.Figure()
fig_line_deaths.add_trace(go.Scatter(x=pv_mort["DATE"], y=pv_mort["DEATHS"],
                                     mode='lines',
                                     name='Total in',
                                     line=dict(color="#EB8C00")
                                     ))

# Create horizontal bar chart (deaths)
fig_bar_mort = px.bar(pv_mort_age, x="DEATHS", y="AGEGROUP", orientation='h')
fig_bar_mort.update_traces(marker_color="#EB8C00")

# Create bar chart (tests)
fig_bar_tests = px.bar(df_tests, x='DATE', y='TESTS')
fig_bar_tests.update_traces(marker_color="#EB8C00")

# Build the Layout of the dashboard
tab_2_layout = html.Div([
    html.Div([
        html.Div(children=[
            dcc.Graph(
                id='map_chart',
                figure=fig_map
            )],
            className="three columns tile"
        ),
        html.Div(children=[
            dcc.Graph(
                id='line_chart_hosp',
                figure=fig_hosp,
                # layout=
            )],
            className="six columns tile"
        ),
        html.Div(children=[
            dcc.Graph(
                id='bar_chart_mort',
                figure=fig_bar_mort
                # layout=
            )],
            className="three columns tile"
        )],
        className="row"
    ),

    html.Div([
        html.Div(children=[
            dcc.Graph(
                id='bar_chart_test',
                figure=fig_bar_tests
                # layout=
            )],
            className="four columns tile"
        ),
        html.Div(children=[
            dcc.Graph(
                id='line_chart_morts',
                figure=fig_line_deaths
                # layout=
            )],
            className="five columns tile"
        ),
        html.Div(children=[
            dcc.Graph(
                id='pie_chart_sex',
                figure=fig_pie,
                # layout=
            )],
            className="three columns tile"
        )],
        className="row"
    ),

    html.Div(id='page-2-content')
])

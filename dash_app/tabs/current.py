import plotly.graph_objects as go

# import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
# from dash.dependencies import Input, Output
# from app import *
import numpy as np
import plotly.express as px
# from urllib.request import urlopen

import json
import pandas as pd

# List of colours for the plots
colours_list = ["#7fc97f", "#beaed4", "#fdc086", "#386cb0", "#f0027f", "#bf5b17", "#ffff99"]
# Title settings
title_font = dict(
    family="Roboto",
    size=14,
    color="#1372B3"
)

# Load CSV files from https://epistat.sciensano.be
URL_epistat = "https://epistat.sciensano.be/Data/"

df_sex = pd.read_csv(URL_epistat + 'COVID19BE_CASES_AGESEX.csv', sep=',', encoding='latin-1')
# df_muni = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_CASES_MUNI.csv', sep=',', encoding='latin-1')
df_muni_cum = pd.read_csv(URL_epistat + 'COVID19BE_CASES_MUNI_CUM.csv', sep=',', encoding='latin-1', dtype={"NIS5": str})
df_hosp = pd.read_csv(URL_epistat + 'COVID19BE_HOSP.csv', sep=',', encoding='latin-1')
df_mort = pd.read_csv(URL_epistat + 'COVID19BE_MORT.csv', sep=',', encoding='latin-1')
df_tests = pd.read_csv(URL_epistat + 'COVID19BE_tests.csv', sep=',', encoding='latin-1')

# replacing na values in df_sex
df_sex["SEX"].fillna("Unknown", inplace=True)
df_sex['SEX'] = df_sex['SEX'].map({"F": "Female", "M": "Male", "Unknown": "Unknown"})

# replacing na values in df_mort
df_mort["SEX"].fillna("Unknown", inplace=True)
df_mort['SEX'] = df_mort['SEX'].map({"F": "Female", "M": "Male", "Unknown": "Unknown"})

## replace na values in df_mort
df_mort["AGEGROUP"].fillna("Unknown", inplace=True)

# PIVOTS
#pv_sex = pd.pivot_table(df_sex, values='CASES', columns=['SEX'], aggfunc=np.sum)
pv_hosp = df_hosp.groupby(['DATE'], as_index=False).sum()
pv_mort = df_mort.groupby(['DATE'], as_index=False).sum()
pv_mort_age = df_mort.groupby(['AGEGROUP'], as_index=False).sum()

# Map data changes
# Replace all less than 5s with 3 and convert data to numeric
df_muni_cum.replace('<5', 3, inplace=True)
df_muni_cum["CASES"] = pd.to_numeric(df_muni_cum["CASES"])
# df_muni_cum["Regions"] = np.where(df_muni_cum["TX_DESCR_NL"] == df_muni_cum["TX_DESCR_FR"],
#                                   df_muni_cum["TX_DESCR_NL"],
#                                   df_muni_cum["TX_DESCR_NL"] + '#' + df_muni_cum["TX_DESCR_FR"])
df_muni_cum['ID'] = df_muni_cum['TX_RGN_DESCR_FR'].map({"Région flamande": "BE2",
                                                        "Région wallonne": "BE3",
                                                        "Région de Bruxelles-Capitale": "BE4"})
df_muni_cum["Regions"] = df_muni_cum['ID'] + df_muni_cum['NIS5']

# Read in geojson
with open("dash_app/assets/municipalities_belgium.geojson") as response:
    municipalities = json.load(response)

df_muni_cum[["NaN", "Provinces1"]] = df_muni_cum["TX_PROV_DESCR_NL"].str.split(" ", expand=True, )
df_muni_cum["Provinces"] = np.where(df_muni_cum["TX_RGN_DESCR_FR"] == "Région de Bruxelles-Capitale", "Brussel", df_muni_cum["Provinces1"])

df_muni_agg = df_muni_cum["CASES"].groupby(df_muni_cum["Provinces"]).sum().reset_index()

with open("dash_app/assets/provinces.geojson") as response:
    provinces = json.load(response)

# Create municipalities map
fig_map_muni = px.choropleth_mapbox(df_muni_cum, geojson=municipalities, locations='Regions', color='CASES',
                                    featureidkey="properties.shn",
                                    mapbox_style="carto-positron",
                                    zoom=7, center={"lat": 50.5039, "lon": 4.4699},
                                    opacity=0.5,
                                    labels={'CASES': 'Cases'},
                                    height=700
                                    )


# Add title to the plot
fig_map_muni.update_layout(
    title_text="Covid_19 cases (count)",
    font=title_font
)


# Create provinces map
fig_map_prov = px.choropleth_mapbox(df_muni_agg, geojson=provinces, locations='Provinces', color='CASES',
                                    featureidkey="properties.province",
                                    mapbox_style="carto-positron",
                                    zoom=7, center={"lat": 50.5039, "lon": 4.4699},
                                    opacity=0.5,
                                    labels={'CASES': 'Cases'},
                                    height=700
                                    )

# Add title to the plot
fig_map_prov.update_layout(
    title_text="Covid_19 cases (count)",
    font=title_font
)

# Create Covid-19 cases (count per day) plot
fig_hosp = go.Figure()
fig_hosp.add_trace(go.Scatter(x=pv_hosp["DATE"], y=pv_hosp["TOTAL_IN"],
                              mode='lines',
                              name='Total in',
                              line=dict(color=colours_list[0])
                              ))
fig_hosp.add_trace(go.Scatter(x=pv_hosp["DATE"], y=pv_hosp["TOTAL_IN_ICU"],
                              mode='lines',
                              name='Total in ICU',
                              line=dict(color=colours_list[1])
                              ))
fig_hosp.add_trace(go.Scatter(x=pv_hosp["DATE"], y=pv_hosp["TOTAL_IN_RESP"],
                              mode='lines',
                              name='Total in resp',
                              line=dict(color=colours_list[2])
                              ))
fig_hosp.add_trace(go.Scatter(x=pv_hosp["DATE"], y=pv_hosp["TOTAL_IN_ECMO"],
                              mode='lines',
                              name='Total in ECMO',
                              line=dict(color=colours_list[3])
                              ))

# Add title to the plot
fig_hosp.update_layout(
    title_text="Covid-19 hospitalisation cases (count per day)",
    xaxis_title="<- Select your time frame by dragging the sliders ->",
    yaxis_title="Number of hospitalised people",
    font=title_font
)

# Add range slider
fig_hosp.update_layout(
    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

# Move legend to the bottom
fig_hosp.update_layout(legend_orientation="h")

# Create line graph (deaths)
fig_line_deaths = go.Figure()
fig_line_deaths.add_trace(go.Scatter(x=pv_mort["DATE"], y=pv_mort["DEATHS"],
                                     mode='lines',
                                     name='Total in',
                                     line=dict(color=colours_list[4])
                                     ))

# Add title to the plot
fig_line_deaths.update_layout(
    title_text="Covid-19 deaths (count per day)",
    xaxis_title="<- Select your time frame by dragging the sliders ->",
    yaxis_title="Number of deaths",
    font=title_font
)

# Add range slider
fig_line_deaths.update_layout(
    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

# Add title to the plot
fig_line_deaths.update_layout(
    title_text="Covid-19 deaths (count per day)",
    # xaxis_title="Date",
    yaxis_title="Number of tests",
    font=title_font
)

# Create bar chart (tests)
fig_bar_tests = px.bar(df_tests, x='DATE', y='TESTS')
fig_bar_tests.update_traces(marker_color=colours_list[5])

# Add title to the plot
fig_bar_tests.update_layout(
    title_text="Covid-19 executed tests (count per day)",
    # xaxis_title="Date",
    yaxis_title="Number of tests",
    font=title_font
)

# Create horizontal bar chart (deaths)
fig_bar_mort = px.bar(pv_mort_age, x="DEATHS", y="AGEGROUP", orientation='h')
fig_bar_mort.update_traces(marker_color=colours_list[5])

# Add title to the plot
fig_bar_mort.update_layout(
    title_text="Covid-19 deaths (total count per age group)",
    xaxis_title="Number of deaths",
    yaxis_title="Age group",
    font=title_font
)

# Create pie charts
fig_pie = px.pie(df_sex, values='CASES', names="SEX",
                 color_discrete_map={
                     "Male": colours_list[0],
                     "Female": colours_list[1],
                     "Unknown": colours_list[2]
                 },
                 height=350)
fig_pie_death = px.pie(df_mort, values='DEATHS', names="SEX",
                       color_discrete_map={
                           "Male": colours_list[0],
                           "Female": colours_list[1],
                           "Unknown": colours_list[2]
                       },
                       height=350)

# Add title to the plot
fig_pie.update_layout(
    title_text="Covid_19 cases (total count per gender)",
    font=title_font
)

fig_pie_death.update_layout(
    title_text="Covid_19 deaths (total count per gender)",
    font=title_font
)


# Build the Layout of the dashboard
tab_layout = html.Div(
    [
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='line_chart_hosp',
                    figure=fig_hosp
                ),
                width=7
            ),
            dbc.Col(
                dcc.Graph(
                    id='bar_chart_test',
                    figure=fig_bar_tests
                ),
                width=5
            )
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='line_chart_morts',
                    figure=fig_line_deaths
                ),
                width=7
            ),
            dbc.Col(
                dcc.Graph(
                    id='bar_chart_mort',
                    figure=fig_bar_mort
                ),
                width=5
            )
        ]),
        dbc.Row([
            dbc.Col(
                [
                    html.Button('Municipalities', id='muni_map', style={"margin-left": "80px"}),
                    html.Button('Provinces', id='prov_map', style={"margin-left": "10px"}),
                    dcc.Graph(id="map_plot", figure={})
                ],
                width=9
            ),
            dbc.Col(
                [
                    dcc.Graph(
                        id='pie_chart_sex',
                        figure=fig_pie
                    ),
                    dcc.Graph(
                        id="pie_chart_death",
                        figure=fig_pie_death
                    )
                ],
                style={'margin-top': "51px"},
                width=3
            )
        ])
    ]
)

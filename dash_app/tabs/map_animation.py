# import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.express as px

import numpy as np
import pandas as pd
from datetime import timedelta
import json

# Title settings
title_font = dict(
    family="Roboto",
    size=14,
    color="#1372B3"
)

# Load CSV files from https://epistat.sciensano.be
URL_epistat = "https://epistat.sciensano.be/Data/"
df_muni = pd.read_csv(URL_epistat + 'COVID19BE_CASES_MUNI.csv', sep=',', encoding='utf-8',
                      dtype={"NIS5": str})

## Municipalities visual
# Remove rows where date is na
df_muni = df_muni[df_muni['DATE'].notna()]
# Replace all less than 5s with 3 and convert data to numeric
df_muni.replace('<5', 3, inplace=True)
df_muni["CASES"] = pd.to_numeric(df_muni["CASES"])
## Add additional ID info per region (to later match with geojson)
df_muni['ID'] = df_muni['TX_RGN_DESCR_FR'].map({"Région flamande": "BE2",
                                                "Région wallonne": "BE3",
                                                "Région de Bruxelles-Capitale": "BE4"})

df_muni["Regions"] = df_muni['ID'] + df_muni['NIS5']


## convert date column date format and extract week number
df_muni['DATE1'] = pd.to_datetime(df_muni['DATE'])
## Calculate latest week
threshhold = max(df_muni['DATE1']).date() - timedelta(8)
#df_muni['WEEK'] = df_muni['WEEK'].dt.week
## get number of cases per week
#df_muni_wk = df_muni["CASES"].groupby([df_muni["Regions"],df_muni['WEEK']]).sum().reset_index()
#df_muni['DATE'] = df_muni['DATE'].apply(lambda x: pd.to_datetime(x))
## extract day of week
#df_muni['DAY'] = df_muni["DATE1"].dt.strftime('%A')
## Calculate cumulative value for each day
#df_muni_cum = df_muni.groupby(['Regions', 'DATE']).sum().groupby(level=0).cumsum().reset_index()
## Calculate cumulative per municipality
#df_muni_wk['CASES_cum'] = df_muni_wk.groupby(['Regions'])['CASES'].apply(lambda x: x.cumsum())
#df_muni_wk['WEEK'] = pd.to_numeric(df_muni["WEEK"])

## filter days after threshhold
is_lastweek = df_muni['DATE1'] > pd.to_datetime(threshhold)
df_muni_vis = df_muni[is_lastweek]

## create cumulatives for this week
#df_muni_vis['CASES_cum'] = df_muni_vis.groupby(['Regions'])['CASES'].apply(lambda x: x.cumsum())

# Read in geojson
with open("dash_app/assets/municipalities_belgium.geojson") as response:
    municipalities = json.load(response)

# Create municipalities map
map_anim_muni = px.choropleth_mapbox(df_muni_vis,
                                     geojson=municipalities,
                                     locations='Regions',
                                     color='CASES',
                                     featureidkey="properties.shn",
                                     mapbox_style="carto-positron",
                                     zoom=7, center={"lat": 50.5039, "lon": 4.4699},
                                     opacity=0.5,
                                     labels={'CASES': 'Cases'},
                                     animation_frame="DATE",
                                     height=700
                                     )

map_anim_muni.update_layout(
    title_text="Timelapse of Covid-19 case withing the last week in Belgian municipalities",
    font=title_font
)

## Provinces view
df_muni[["NaN", "Provinces1"]] = df_muni["TX_PROV_DESCR_NL"].str.split(" ", expand=True, )
df_muni["Provinces"] = np.where(df_muni["TX_RGN_DESCR_FR"] == "Région de Bruxelles-Capitale", "Brussel",
                                df_muni["Provinces1"])

df_prov = df_muni["CASES"].groupby([df_muni["Provinces"], df_muni['DATE']]).sum().reset_index()
df_prov['DATE1'] = pd.to_datetime(df_prov['DATE'])

is_lastweek_prov = df_prov['DATE1'] > pd.to_datetime(threshhold)
df_prov_vis = df_prov[is_lastweek_prov]

# Read in geojson
with open("dash_app/assets/provinces.geojson") as response:
    provinces = json.load(response)

# Create municipalities map
map_anim_prov = px.choropleth_mapbox(df_prov_vis,
                                     geojson=provinces,
                                     locations='Provinces',
                                     color='CASES',
                                     featureidkey="properties.province",
                                     mapbox_style="carto-positron",
                                     zoom=7, center={"lat": 50.5039, "lon": 4.4699},
                                     opacity=0.5,
                                     labels={'CASES': 'Cases'},
                                     animation_frame="DATE",
                                     height=700
                                     )

map_anim_prov.update_layout(
    title_text="Timelapse of Covid-19 case withing the last week in Belgian provinces",
    font=title_font
)



# Build the Layout of the dashboard
tab_layout = html.Div(
    [
        dbc.Row(
            dbc.Col([
                html.H2("Municipalities View"),
                dcc.Graph(figure=map_anim_muni)
            ],
                width=12
            )
        ),
        dbc.Row(
            dbc.Col([
                html.H2("Province View"),
                dcc.Graph(figure=map_anim_prov)
            ],
            width=12)
        )
    ]
)
# import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.express as px

import numpy as np
import pandas as pd
from datetime import date
import calendar
import json

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


## convert date column date format
#df_muni['DATE'] = df_muni['DATE'].replace(r'\\n', '', regex=True)
#print(type(df_muni['DATE']))
df_muni['DATE'] = pd.to_datetime(str(df_muni['DATE']), format='%Y-%m-%d')
#df_muni['DATE'] = pd.to_datetime("01/03/2020")
#df_muni['DATE'] = df_muni['DATE'].apply(lambda x: pd.to_datetime(x))
## extract day of week
df_muni['DAY'] = df_muni["DATE"].apply(lambda x: x.strftime('%A'))
## Calculate cumulative value for each day
#df_muni_cum = df_muni.groupby(['Regions', 'DATE']).sum().groupby(level=0).cumsum().reset_index()
## Calculate cumulative per municipality
df_muni['CASES_cum'] = df_muni.groupby(['Regions'])['CASES'].apply(lambda x: x.cumsum())

## filter on sundays
is_Sunday =df_muni['DAY']=='Sunday'
df_muni_plot = df_muni[is_Sunday]

# Read in geojson
with open("dash_app/assets/municipalities_belgium.geojson") as response:
    municipalities = json.load(response)

# Create municipalities map
map_anim_muni = px.choropleth_mapbox(df_muni_plot,
                                     geojson=municipalities,
                                     locations='Regions',
                                     color='CASES_cum',
                                     featureidkey="properties.shn",
                                     mapbox_style="carto-positron",
                                     zoom=7, center={"lat": 50.5039, "lon": 4.4699},
                                     opacity=0.5,
                                     labels={'CASES_cum': 'Cases'},
                                     animation_frame="DATE",
                                     height=700
                                     )


## Provinces view
df_muni[["NaN", "Provinces1"]] = df_muni["TX_PROV_DESCR_NL"].str.split(" ", expand=True, )
df_muni["Provinces"] = np.where(df_muni["TX_RGN_DESCR_FR"] == "Région de Bruxelles-Capitale", "Brussel",
                                    df_muni["Provinces1"])

df_muni_agg = df_muni["CASES"].groupby(df_muni["Provinces"]).sum().reset_index()

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
            html.H5("Province View")
        )
    ]
)
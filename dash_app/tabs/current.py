import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
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
df_sex = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_CASES_AGESEX.csv', sep=',', encoding='latin-1')
# df_muni = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_CASES_MUNI.csv', sep=',', encoding='latin-1')
df_muni_cum = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_CASES_MUNI_CUM.csv', sep=',', encoding='latin-1')
df_hosp = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_HOSP.csv', sep=',', encoding='latin-1')
df_mort = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_MORT.csv', sep=',', encoding='latin-1')
df_tests = pd.read_csv('https://epistat.sciensano.be/Data/COVID19BE_tests.csv', sep=',', encoding='latin-1')

# replacing na values in df_sex
df_sex["SEX"].fillna("Unknown", inplace=True)
df_sex['SEX'] = df_sex['SEX'].map({"F":"Female", "M":"Male"})

# PIVOTS
pv_sex = pd.pivot_table(df_sex, values='CASES', columns=['SEX'], aggfunc=np.sum)
pv_hosp = df_hosp.groupby(['DATE'], as_index=False).sum()
pv_mort = df_mort.groupby(['DATE'], as_index=False).sum()
pv_mort_age = df_mort.groupby(['AGEGROUP'], as_index=False).sum()

# Map data changes
# Replace all less than 5s with 3 and convert data to numeric
df_muni_cum.replace('<5', 3, inplace=True)
df_muni_cum["CASES"] = pd.to_numeric(df_muni_cum["CASES"])

# Read in geojson
with open("dash_app/assets/municipalities_belgium.geojson") as response:
    municipalities = json.load(response)

# Create a map
fig_map = px.choropleth_mapbox(df_muni_cum, geojson=municipalities, locations='TX_DESCR_NL', color='CASES',
                               featureidkey="properties.name",
                               mapbox_style="carto-positron",
                               zoom=6, center={"lat": 50.5039, "lon": 4.4699},
                               opacity=0.5,
                               labels={'CASES': 'Cases'}
                               )

# Add title to the plot
fig_map.update_layout(
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
    #xaxis_title="Date",
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
    #xaxis_title="Date",
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
    #xaxis_title="Date",
    yaxis_title="Number of tests",
    font=title_font
)

# Create bar chart (tests)
fig_bar_tests = px.bar(df_tests, x='DATE', y='TESTS')
fig_bar_tests.update_traces(marker_color=colours_list[5])

# Add title to the plot
fig_bar_tests.update_layout(
    title_text="Covid-19 executed tests (count per day)",
    #xaxis_title="Date",
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

# Create pie chart
fig_pie = px.pie(df_sex, values='CASES', title="Cases by sex", names="SEX")

# Adjust display
fig_pie.update_traces(marker=dict(colors=colours_list))

# Add title to the plot
fig_pie.update_layout(
    title_text="Covid_19 cases (total count per gender)",
    font=title_font
)


# Build the Layout of the dashboard
tab_2_layout = html.Div(
    [
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='line_chart_hosp',
                    figure=fig_hosp
                ),
                width=6
            ),
            dbc.Col(
                dcc.Graph(
                    id='bar_chart_test',
                    figure=fig_bar_tests
                ),
                width=3
            ),
            dbc.Col(
                dcc.Graph(
                    id='map_chart',
                    figure=fig_map
                ),
                width=3
            )
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='line_chart_morts',
                    figure=fig_line_deaths
                ),
                width=6
            ),
            dbc.Col(
                dcc.Graph(
                    id='bar_chart_mort',
                    figure=fig_bar_mort
                ),
                width=3
            ),
            dbc.Col(
                dcc.Graph(
                    id='pie_chart_sex',
                    figure=fig_pie
                ),
                width=3
            )
        ])
    ]
)

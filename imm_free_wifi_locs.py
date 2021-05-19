#!/usr/bin/python3
# -*- coding: utf-8 -*-

from folium import Map, GeoJson
from geojson import Feature, FeatureCollection
from h3 import h3

import branca.colormap as cm
import datapane as dp
import folium
import json
import os
import pandas as pd

# Hide warnings
import warnings
warnings.filterwarnings('ignore')

dp.login('YOUR_TOKEN')

dat = pd.read_csv(os.path.dirname(os.path.abspath(__file__)) + '/data/ibb_wifi_new_user_data.csv')

# I do not like uppercase :)
dat.columns = ['_id', 'subscription_date', 'subscription_county', 'subscription_type', 'lon', 'lat',
               'number_of_subscription']
# Converting from Turkish to English for Subscription Type column
# dat['subscription_type'].unique()
dat['subscription_type'] = dat['subscription_type'].map(
    {'Yerli': 'domestic', 'Yabancı': 'foreign', 'Bilinmiyor': 'unknown'})
# Changing data type for date column, str -> timestamp
dat['subscription_date'] = pd.to_datetime(dat['subscription_date'])

dat_coord = dat[['lon', 'lat', 'number_of_subscription']].groupby(['lon', 'lat']).sum().reset_index()
dat_coord['hex_id'] = dat_coord.apply(lambda row: h3.geo_to_h3(row["lat"], row["lon"], 8), axis=1)
df_aggreg = dat_coord[['hex_id', 'number_of_subscription']].groupby('hex_id').sum().reset_index()
df_aggreg.rename(columns={'number_of_subscription': 'value'}, inplace=True)

df_aggreg["geometry"] = df_aggreg.hex_id.apply(
    lambda x: {"type": "Polygon", "coordinates": [h3.h3_to_geo_boundary(h=x, geo_json=True)]})


def plot_free_wifi_locations(df):
    # generate a new map
    folium_map = folium.Map(location=[41.013611, 28.955],
                            zoom_start=10,
                            tiles="CartoDB dark_matter")

    # for each row in the data, add a circle marker
    for index, row in df.iterrows():
        # add marker to the map
        folium.CircleMarker(location=(row["lat"],
                                      row["lon"]),
                            radius=1,
                            color="#E37222",
                            fill=True).add_to(folium_map)
    return folium_map


def hexagons_dataframe_to_geojson(df_hex, file_output=None):
    """
    Produce the GeoJSON for a dataframe that has a geometry column in geojson 
    format already, along with the columns hex_id and value
    
    """
    list_features = []

    for i, row in df_hex.iterrows():
        feature = Feature(geometry=row["geometry"], id=row["hex_id"], properties={"value": row["value"]})
        list_features.append(feature)

    feat_collection = FeatureCollection(list_features)

    geojson_result = json.dumps(feat_collection)

    # optionally write to file
    if file_output is not None:
        with open(file_output, "w") as f:
            json.dump(feat_collection, f)

    return geojson_result


def choropleth_map(df_aggreg, border_color='black', fill_opacity=0.7, initial_map=None, with_legend=False,
                   kind="linear"):
    """
    Creates choropleth maps given the aggregated data.
    """
    # colormap
    min_value = df_aggreg["value"].min()
    max_value = df_aggreg["value"].max()
    m = round((min_value + max_value) / 2, 0)

    # take resolution from the first row
    res = h3.h3_get_resolution(df_aggreg.loc[0, 'hex_id'])

    if initial_map is None:
        initial_map = Map(location=[41, 29], zoom_start=11, tiles="cartodbpositron",
                          attr='© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="http://cartodb.com/attributions#basemaps">CartoDB</a>'
                          )

    # the colormap
    custom_cm = cm.StepColormap(['#fcd2d2', '#ffb2b2', '#ff7f7f', '#fa5252', '#ff0000'], vmin=min_value, vmax=max_value)

    # create geojson data from dataframe
    geojson_data = hexagons_dataframe_to_geojson(df_hex=df_aggreg)

    # plot on map
    name_layer = "Choropleth " + str(res)
    if kind != "linear":
        name_layer = name_layer + kind

    GeoJson(
        geojson_data,
        style_function=lambda feature: {
            'fillColor': custom_cm(feature['properties']['value']),
            'color': border_color,
            'weight': 1,
            'fillOpacity': fill_opacity
        },
        name=name_layer
    ).add_to(initial_map)
    # add legend (not recommended if multiple layers)
    if with_legend is True:
        custom_cm.add_to(initial_map)

    return initial_map


pointmap = plot_free_wifi_locations(dat_coord)
hexmap = choropleth_map(df_aggreg=df_aggreg, with_legend=True)

page1 = dp.Page(title='Point Map', blocks=['## Point Map for IMM Free Wifi Locations', pointmap])
page2 = dp.Page(title='Hexagon Map',
                blocks=['## Hexagon Map with Number of Subscription for IMM Free Wifi Locations', hexmap])

"""
# the other representation
report = []
report.append(dp.Markdown(f'''Point Map for IMM Free Wifi Locations'''))
report.append(dp.Plot(pointmap))

report.append(dp.Markdown(f'''Hexagon Map with Number of Subscription for IMM Free Wifi Locations'''))
report.append(dp.Plot(hexmap))

dp.Report(*report).publish(name='IMM Free Wifi Locations', headline='Interactive Leaflet Map Visualization with Folium in Python')
"""

dp.Report(page1, page2).publish(name='IMM Free Wifi Locations',
                                headline='Interactive Leaflet Map Visualization with Folium in Python')
dp.logout()

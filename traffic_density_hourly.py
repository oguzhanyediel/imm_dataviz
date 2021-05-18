#!/usr/bin/python3
# -*- coding: utf-8 -*-

import config
import logging
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import utils

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('IMM Data Visualization - Traffic Density')


def data_preparation():
    """
    :rtype: dataframe
    """
    # getting data
    dat = utils.getting_raw_data(dat_name='tdh', url_list=True)
    dat.reset_index(drop=True, inplace=True)
    dat.columns = [c.lower() for c in dat.columns]
    dat['date_time'] = pd.to_datetime(dat['date_time'])
    return dat


def creating_heatmap_data(dat):
    """
    :param dat: dataframe
    :rtype: dataframe
    """
    data = dat[['date_time', 'number_of_vehicles']].groupby('date_time').sum().reset_index()
    data['year'] = data['date_time'].apply(lambda row: row.year)
    data['month'] = data['date_time'].apply(lambda row: row.month_name())
    data['day'] = data['date_time'].apply(lambda row: row.day_name())
    data['hour'] = data['date_time'].apply(lambda row: row.hour)
    return data


def df_to_plotly_heatmap_data(df):
    """
    :param df: dataframe
    :rtype: dict
    """
    return {'z': df.values.tolist(), 'x': df.columns.tolist(), 'y': df.index.tolist()}


def creating_heatmap_graph(df, year, month):
    """
    :param df: dataframe
    :param year: int
    :param month: string
    :return: Plotly Heatmap Graph
    """
    df_ = df[(df['year'] == year) & (df['month'] == month)].reset_index(drop=True)

    # grouping
    df_grouped = df_[['day', 'hour', 'number_of_vehicles']] \
        .groupby(['day', 'hour']).mean().reset_index() \
        .rename(columns={'number_of_vehicles': 'avg_number_of_vehicles'})

    # rounding
    df_grouped['avg_number_of_vehicles'] = round(df_grouped['avg_number_of_vehicles'], 4)

    # creating pivot data
    df_pivot = pd.pivot_table(data=df_grouped, values='avg_number_of_vehicles', index='day', columns='hour')

    # vis
    fig = go.Figure(data=go.Heatmap(df_to_plotly_heatmap_data(df_pivot.reindex(config.days)),
                                    colorbar=dict(title='Avg Number of Vehicles')))

    # arrangements
    fig.update_layout(
        title='Traffic Density Heatmap by Day & Hour [{0} - {1}]'.format(month, year),
        xaxis=dict(
            dtick=1
        ),
        xaxis_title='Hour',
        yaxis_title='Days',
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        )
    )

    return fig.show()


def main():
    """
    :return: Plotly Figure
    """
    df = data_preparation()

    # The localhost page is opened on the Internet browser.
    # Each plot is presented in a separate browser tab.
    # graph part I
    data = creating_heatmap_data(dat=df)
    for m in config.tdh_months:
        for y in config.tdh_years:
            creating_heatmap_graph(df=data.copy(), year=y, month=m)


def putting_into_datapane():
    return


def putting_into_streamlit():
    return


if __name__ == "__main__":
    main()

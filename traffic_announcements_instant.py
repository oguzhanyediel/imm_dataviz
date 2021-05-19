#!/usr/bin/python3
# -*- coding: utf-8 -*-

import config
import logging
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import utils

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('IMM Data Visualization - Traffic Announcements')


def creating_datetime_col(df, col_name):
    """
    :param df: dataframee
    :param col_name: string
    :return: None
    """
    df[col_name] = df[col_name].apply(lambda row: row[:19])
    df[col_name] = pd.to_datetime(df[col_name])


def data_preparation():
    """
    :return: dataframe
    """
    # getting data
    data = utils.getting_raw_data(dat_name='tai')
    data.columns = [c.lower() for c in data.columns]
    creating_datetime_col(data, 'announcement_starting_datetime')
    creating_datetime_col(data, 'announcement_ending_datetime')
    data['announcement_type_desc'] = data['announcement_type_desc'].map(config.announcement_type_desc)
    return data[data['announcement_type_desc'].isin(config.atd_list)][
        ['announcement_starting_datetime', 'announcement_ending_datetime', 'announcement_type_desc']].reset_index(
        drop=True)


def creating_line_graph(df):
    """
    :param df: dataframe
    :return: Plotly Line Graph
    """
    df['date'] = df['announcement_starting_datetime'].dt.strftime('%Y-%m')
    df['count'] = 1
    df_ = df[['date', 'announcement_type_desc', 'count']].groupby(
        ['date', 'announcement_type_desc']).sum().reset_index()
    data_pivot = pd.pivot_table(df_, values='count', index=['date'], columns='announcement_type_desc',
                                aggfunc=np.sum, fill_value=0)

    fig = go.Figure()
    for c in data_pivot.columns:
        fig.add_trace(go.Scatter(x=data_pivot.index, y=data_pivot[c].values, name=c, mode='lines',
                                 line=dict(shape='linear'), connectgaps=True, showlegend=True))

    fig.update_layout(
        title='Total Announcement Count by Month',
        xaxis_title='Month',
        yaxis_title='Total Announcement Count',
        legend_title="Announcement Type",
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        )
    )
    fig.show()


def creating_bar_graph_data(df):
    """
    :param df: dataframe
    :rtype: dataframe
    """
    df['year'] = df['announcement_starting_datetime'].apply(lambda row: row.year)
    df['month'] = df['announcement_starting_datetime'].apply(lambda row: row.month_name())
    df['count'] = 1
    df_ = df[['year', 'month', 'announcement_type_desc', 'count']].groupby(
        ['year', 'month', 'announcement_type_desc']).sum().reset_index()
    return df_


def creating_bar_graph(df, type_, year=2020, month=None):
    """
    :param df: dataframe
    :param type_: string
    :param year: int
    :param month: string
    :return: Plotly Bar Graph
    """
    if month is None:
        # plot params
        y_ = 'total_count'
        y_labels = 'Total Count'
        title_ = '{0} - Comparison of Total Announcement Count based on Months [{1}]'.format(type_, year)
        yt_ = 'Total [{0}] Count'.format(type_)

        # data grouping for plot
        df_ = df[(df['year'] == year) & (df['announcement_type_desc'] == type_)][
            ['year', 'month', 'announcement_type_desc', 'count']] \
            .groupby(['year', 'month', 'announcement_type_desc']) \
            .sum().reset_index() \
            .rename(columns={'count': 'total_count'})
        df_grouped = df_.set_index('month').reindex([key for key in config.months]).reset_index()[
            ['month', 'total_count']]
    else:
        # plot params
        y_ = 'avg_count'
        y_labels = 'Avg Count'
        title_ = '{0} - Comparison of Average Announcement Count based on Months [2017 December - 2021 March]'.format(
            type_)
        yt_ = 'Avg [{0}] Count'.format(type_)

        # data grouping for plot
        df_grouped = df[(df['month'].isin(month)) & (df['announcement_type_desc'] == type_)][
            ['month', 'announcement_type_desc', 'count']] \
            .groupby(['month', 'announcement_type_desc']) \
            .mean().reset_index() \
            .rename(columns={'count': 'avg_count'})[['month', 'avg_count']]
        df_grouped['avg_count'] = round(df_grouped['avg_count'], 2)

    fig = px.bar(df_grouped, x='month', y=y_, color=y_, labels={y_: y_labels},
                 color_continuous_scale=px.colors.sequential.Jet, opacity=0.8)

    fig.update_layout(
        title=title_,
        xaxis=dict(
            tickangle=0,
            dtick=1
        ),
        xaxis_title='Month',
        yaxis_title=yt_,
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        )
    )
    fig.show()


def main():
    """
    :return: Plotly Figure
    """
    df = data_preparation()

    # The localhost page is opened on the Internet browser.
    # Each plot is presented in a separate browser tab.
    # graph part I
    creating_line_graph(df)

    # graph part II
    df_ = creating_bar_graph_data(df)
    for t in config.atd_list:
        creating_bar_graph(df=df_, type_=t, month=['March', 'July', 'October'])
        for y in config.tai_years:
            creating_bar_graph(df=df_, type_=t, year=y)

    # graph part III


def putting_into_datapane():
    return


def putting_into_streamlit():
    return


if __name__ == "__main__":
    main()

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import config
import datapane as dp
import logging
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
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
        ),
        width=900,
        height=650
    )
    return fig


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
        title_ = '{0} - Comparison of Average Announcement Count based on Months [2018 January - 2021 April)'.format(
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
        ),
        width=900,
        height=650
    )
    return fig


def creating_scatter_graph_data(data):
    """
    :param data: dataframe
    :rtype: dataframe
    """
    # It will be relocated the position of time columns for the records that have a negative date difference.
    # (announcement_ending_datetime - announcement_starting_datetime) < 0
    # There were 122 incorrect records
    data['diff_sec'] = (data.announcement_ending_datetime - data.announcement_starting_datetime).astype(
        'timedelta64[s]')

    # base columns
    col_list = ['announcement_starting_datetime', 'announcement_ending_datetime', 'announcement_type_desc']

    # getting normal records
    data_ = pd.DataFrame(columns=col_list)
    data_ = data_.append(data[data['diff_sec'] > 0][col_list].reset_index(drop=True))

    # transforming abnormal records
    change_data = data[data['diff_sec'] < 0][
        ['announcement_ending_datetime', 'announcement_starting_datetime', 'announcement_type_desc']].reset_index(
        drop=True)
    change_data.columns = col_list
    data_ = data_.append(change_data)

    # adding diff seconds again
    data_['diff_sec'] = (data_.announcement_ending_datetime - data_.announcement_starting_datetime).astype(
        'timedelta64[s]')
    data_.reset_index(drop=True, inplace=True)
    return data_


def grouping_types(df, t):
    """
    :param df: dataframe
    :param t: string; diff_sec, diff_min or diff_hhh
    :rtype: dataframe
    """
    dat = df[['announcement_type_desc', t]] \
        .groupby('announcement_type_desc') \
        .mean().reset_index() \
        .rename(columns={t: 'avg_{0}'.format(t[-3:])})
    return dat


def creating_scatter_graph(df, type_, marker_size=50):
    """
    :param df: dataframe
    :param type_: string
    :param marker_size: int
    :return: Plotly Scatter Graph
    """
    # getting grouping data
    df_ = grouping_types(df=df.copy(), t=type_)

    # changing numeric column name
    t = 'avg_' + type_[-3:]

    # finding the marker size for announcement types
    df_type = df_.sort_values(t)
    df_type['coeff'] = round(-(df_type[t].shift(1) - df_type[t]), 2)
    df_type.reset_index(drop=True, inplace=True)
    df_type['coeff'][0] = 0  # there is nan value in the first cell because of shift function
    df_type['change'] = round(df_type['coeff'] / df_type[t], 2)

    # vis
    size_ = [marker_size + (marker_size * i) for i in df_type['change'].tolist()]
    color_ = [i for i in range(0, len(df_type))]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_type['announcement_type_desc'], y=df_type[t],
                             mode='markers', marker=dict(size=size_, color=color_)))
    fig.update_layout(
        title='Average Duration Between the Start and End Time of Announcements [{0}]'.format(t[-3:-2]),
        xaxis_title='Announcement Type Description',
        yaxis_title='Avg Duration [{0}]'.format(t[-3:-2]),
        legend_title="Announcement Type",
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        ),
        width=900,
        height=650
    )
    return fig


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
        creating_bar_graph(df=df_.copy(), type_=t, month=['March', 'July', 'October'])
        for y in config.tai_years:
            creating_bar_graph(df=df_.copy(), type_=t, year=y)

    # graph part III
    data_ = creating_scatter_graph_data(df)
    data_['diff_min'] = round(data_['diff_sec'] / 60, 2)
    data_['diff_hhh'] = round(data_['diff_min'] / 60, 2)
    # fig = px.box(data_, x='announcement_type_desc', y='diff_min')
    # fig.show()
    creating_scatter_graph(df=data_, type_='diff_min')


def putting_into_streamlit():
    """
    :return: None
    """
    df = data_preparation()

    st.markdown("## **:loudspeaker: Transportation Management Center Traffic Announcement Data Visualization**")
    st.write(creating_line_graph(df))

    df_ = creating_bar_graph_data(df)
    # Please use the config.atd_list for all announcement type descriptions
    for t in config.atd_list_:
        # It can be given desired months in the month variable
        st.write(creating_bar_graph(df=df_.copy(), type_=t, month=['March', 'July', 'October']))
        for y in config.tai_years:
            st.write(creating_bar_graph(df=df_.copy(), type_=t, year=y))

    data_ = creating_scatter_graph_data(df)
    data_['diff_min'] = round(data_['diff_sec'] / 60, 2)
    data_['diff_hhh'] = round(data_['diff_min'] / 60, 2)
    st.write(creating_scatter_graph(df=data_, type_='diff_min'))


def putting_into_datapane():
    """
    :return: None
    """
    # getting token
    dp.login(config.dp_token)

    # getting data
    df = data_preparation()

    # line graph
    p1 = creating_line_graph(df)
    dp.Report(dp.Plot(p1)).publish(name='Total Announcement Count', open=True)

    # bar graph
    df_ = creating_bar_graph_data(df)
    bplot1 = creating_bar_graph(df=df_.copy(), type_='Accident Notification', year=2019)
    bp1 = dp.Page(title='Accident Notification - 2019', blocks=[bplot1])
    bplot2 = creating_bar_graph(df=df_.copy(), type_='Accident Notification', year=2020)
    bp2 = dp.Page(title='Accident Notification - 2020', blocks=[bplot2])
    dp.Report(bp1, bp2).publish('Comparison of Total Accident Notification Count', open=True)

    # bar graph 2
    p2 = creating_bar_graph(df=df_.copy(), type_='Vehicle Breakdown', month=['March', 'July', 'October'])
    dp.Report(dp.Plot(p2)).publish(name='Vehicle Breakdown - Comparison of Average Count', open=True)

    # scatter graph
    data_ = creating_scatter_graph_data(df)
    data_['diff_min'] = round(data_['diff_sec'] / 60, 2)
    p3 = creating_scatter_graph(df=data_, type_='diff_min')
    dp.Report(dp.Plot(p3)).publish(name='Average Duration Between the Start and End Time of Announcements', open=True)

    dp.logout()


if __name__ == "__main__":
    # main()
    putting_into_streamlit()
    # putting_into_datapane()

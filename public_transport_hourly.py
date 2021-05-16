#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import config
import io
import json
import logging
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import requests
import sys
import utils

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('IMM Data Visualization - Hourly Public Transport')


def data_preparation():
    # getting data
    dat = utils.getting_raw_data(dat_name='pth', url_list=True)
    dat.reset_index(drop=True, inplace=True)
    dat.columns = [c.lower() for c in dat.columns]

    # Converting from Turkish to English for Subscription Type column
    dat['transport_type_desc'] = dat['transport_type_desc'].map({'KARAYOLU': 'Highway', 'RAY': 'Rail', 'DENİZ': 'Sea'})
    dat['transfer_type'] = dat['transfer_type'].map({'AKTARMA': 'Transmission', 'NORMAL': 'Normal'})

    # Changing data type for date column, str -> timestamp
    dat['date_time'] = pd.to_datetime(dat['date_time'])

    # T5 EMİNÖNÜ-ALİBEYKÖY; This line has opened to use this year, so it will be excluded from data.
    # KABATAŞ-MAHMUTBEY; And this line has very limited usage in 2020, so it will be excluded from data.
    data = dat[dat['line'].isin(['T5 EMİNÖNÜ-ALİBEYKÖY', 'KABATAŞ-MAHMUTBEY']) == False].reset_index(drop=True)
    data['month'] = data['date_time'].apply(lambda row: row.month_name())
    data['year'] = data['date_time'].apply(lambda row: row.year)
    return data


def data_generator(data, year, month):
    """
    :param data: dataframe
    :param year: int
    :param month: string
    :rtype: dataframe
    """
    return data[(data['year'] == year) & (data['month'] == month)][
        ['date_time', 'number_of_passenger', 'number_of_passage']].groupby('date_time').sum().reset_index()


def creating_daily_data(df):
    """
    :param df: dataframe
    :rtype: dataframe
    """
    df['day_value'] = df['date_time'].apply(lambda row: row.date().day)
    return df[['day_value', 'number_of_passenger', 'number_of_passage']].groupby('day_value').sum().reset_index()


def creating_day_avg_data(df):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    df['day_value'] = df['date_time'].apply(lambda row: row.day_name())
    df_grouped = df[['day_value', 'number_of_passenger', 'number_of_passage']] \
        .groupby('day_value') \
        .mean().reset_index().round(2) \
        .rename(columns={'number_of_passenger': 'avg_number_of_passenger',
                         'number_of_passage': 'avg_number_of_passage'})
    return df_grouped.groupby(['day_value']).sum().reindex(days).reset_index()


def creating_line_graph_based_day(df_2020, df_2021, col, m=1):
    """
    :param df_2020: dataframe
    :param df_2021: dataframe
    :param col: string
    :param m: int, month number; 1 or 2
    :return: Plotly Line Graph
    """
    if col == 'number_of_passenger':
        title_ = 'Daily Passenger Count'
        yxs = 'Passenger Count'
        nm = 'Passenger Count'
    elif col == 'avg_number_of_passenger':
        title_ = 'Daily Average Passenger Count'
        yxs = 'Avg Passenger Count'
        nm = 'Avg Passenger Count'
    elif col == 'number_of_passage':
        title_ = 'Daily Passage Count'
        yxs = 'Passage Count'
        nm = 'Passage Count'
    else:
        title_ = 'Daily Average Passage Count'
        yxs = 'Avg Passage Count'
        nm = 'Avg Passage Count'

    if m == 2:
        nm_month = 'February'
    else:
        nm_month = 'January'

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_2020['day_value'], y=df_2020[col], line=dict(color='royalblue'),
                             showlegend=True, name=nm + ' - {0} 2020'.format(nm_month), mode='lines'))
    fig.add_trace(go.Scatter(x=df_2021['day_value'], y=df_2021[col], line=dict(color='firebrick'),
                             showlegend=True, name=nm + ' - {0} 2021'.format(nm_month), mode='lines'))

    fig.update_layout(
        title=title_,
        xaxis_title='Day',
        yaxis_title=yxs,
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        )
    )
    return fig.show()


def creating_bar_graph_data(bar_part, base_data, y, m, t='Highway'):
    """
    :param bar_part: string
    :param base_data: dataframe
    :param y: int
    :param m: string
    :param t: string
    :rtype: dataframe
    """
    if bar_part == 'tt_general':
        bar_ = base_data[['year', 'month', 'transport_type_desc', 'number_of_passenger', 'number_of_passage']]
        bar_dat = bar_.groupby(['year', 'month', 'transport_type_desc']).sum().reset_index()
        bar_data = bar_dat[(bar_dat['year'] == y) & (bar_dat['month'] == m)].reset_index(drop=True)
        bar_data['number_of_passenger_perc'] = round(
            bar_data['number_of_passenger'] / bar_data['number_of_passenger'].sum(), 2)
        bar_data['number_of_passage_perc'] = round(bar_data['number_of_passage']/bar_data['number_of_passage'].sum(), 2)
    else:  # tt_in_details
        bar_ = base_data[['year', 'month', 'transport_type_desc', 'line', 'number_of_passenger', 'number_of_passage']]
        bar_dat = bar_.groupby(['year', 'month', 'transport_type_desc', 'line']).sum().reset_index()
        bar_data = bar_dat[
            (bar_dat['year'] == y) & (bar_dat['month'] == m) & (bar_dat['transport_type_desc'] == t)].reset_index(
            drop=True)
    return bar_data


def creating_bar_graph_based_transport_type(dat, col):
    """
    :param dat: dataframe
    :param col: string
    :return: Plotly Bar Graph
    """
    for m in config.pth_months:
        data = pd.DataFrame()
        for y in config.pth_years:
            data = data.append(creating_bar_graph_data(bar_part='tt_general', base_data=dat, y=y, m=m))
        data['date'] = data.apply(lambda row: row['month'] + ' ' + str(row['year']), axis=1)
        data.reset_index(drop=True, inplace=True)

        # vis
        if col == 'number_of_passenger':
            y_ = col
            text_ = col + '_perc'
            title_ = 'Passenger Count by Transport Type'
            yaxis_title_ = 'Passenger Count'
        else:  # number_of_passage
            y_ = col
            text_ = col + '_perc'
            title_ = 'Passage Count by Transport Type'
            yaxis_title_ = 'Passage Count'

        fig = px.bar(x=data['transport_type_desc'], color=data['date'], y=data[y_], text=data[text_], title=title_,
                     barmode='group')
        fig.update_layout(xaxis_title='Type', yaxis_title=yaxis_title_)
        fig.show()


def creating_bar_graph_based_transport_type_in_details(dat, value_type, type_desc):
    """
    :param dat: dataframe
    :param value_type: string
    :param type_desc: string
    :return: Plotly Bar Graph
    """
    if value_type == 'number_of_passenger':
        title_ = 'Passenger Count by Transport Line'
        yxs = 'Passenger Count'
    else:
        title_ = 'Passage Count by Transport Line'
        yxs = 'Passage Count'

    for m in config.pth_months:
        data = pd.DataFrame()
        for y in config.pth_years:
            data = data.append(creating_bar_graph_data(bar_part='tt_in_details', base_data=dat.copy(), y=y, m=m,
                                                       t=type_desc))
        data['date'] = data.apply(lambda row: row['month'] + ' ' + str(row['year']), axis=1)
        data.reset_index(drop=True, inplace=True)

        fig = px.bar(data, x='line', color='date',
                     color_discrete_map={
                         data['date'].unique().tolist()[0]: 'purple',
                         data['date'].unique().tolist()[1]: '#08e8de'
                         },
                     y=value_type, title=title_, barmode='group')
        fig.update_layout(xaxis_title='Line', yaxis_title=yxs)
        fig.show()


def main():
    df = data_preparation()

    # The localhost page is opened on the Internet browser.
    # Each plot is presented in a separate browser tab.
    for m in config.pth_months:
        df_20 = data_generator(data=df, year=2020, month=m)
        df_21 = data_generator(data=df, year=2021, month=m)
        for col in config.pth_cols:
            if m == 'February':
                m_ = 2
            else:
                m_ = 1
            creating_line_graph_based_day(creating_daily_data(df_20.copy()),
                                          creating_daily_data(df_21.copy()),
                                          col=col, m=m_)
            creating_line_graph_based_day(creating_day_avg_data(df_20.copy()),
                                          creating_day_avg_data(df_21.copy()),
                                          col='avg_' + col, m=m_)
    for col in config.pth_cols:
        creating_bar_graph_based_transport_type(dat=df.copy(), col=col)
    for col in config.pth_cols:
        for t in config.pth_types:
            creating_bar_graph_based_transport_type_in_details(dat=df.copy(), value_type=col, type_desc=t)


if __name__ == "__main__":
    main()

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import config
import io
import json
import logging
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import requests
import sys
import utils

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('IMM Data Visualization - Hourly Public Transport')


def data_preparation():
    """
    :rtype: dataframe
    """
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


def data_generator(data, year, month, is_line=False):
    """
    :param data: dataframe
    :param year: int
    :param month: string
    :param is_line: bool
    :rtype: dataframe
    """
    grouping_cols = ['date_time']
    cols = ['date_time', 'number_of_passenger', 'number_of_passage']
    if is_line is True:
        grouping_cols.append('line')
        cols.append('line')
    return data[(data['year'] == year) & (data['month'] == month)][cols].groupby(grouping_cols).sum().reset_index()


def creating_daily_data(df):
    """
    :param df: dataframe
    :rtype: dataframe
    """
    df['day_value'] = df['date_time'].apply(lambda row: row.date().day)
    return df[['day_value', 'number_of_passenger', 'number_of_passage']].groupby('day_value').sum().reset_index()


def creating_day_avg_data(df):
    """
    :param df: dataframe
    :rtype: dataframe
    """
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


def creating_avg_data_all_date_breakdown(df, lines, time_type, d=None, h=None):
    """
    :param df: dataframe
    :param lines: list
    :param time_type: string
    :param d: list
    :param h: list
    :rtype: dataframe
    """
    # Homework :]
    # Please run the same method again, combining the d and h parameters in a single parameter
    # Hint: data type comparison
    df['day_value'] = df['date_time'].apply(lambda row: row.day_name())
    df['hour'] = df['date_time'].apply(lambda row: row.hour)
    df_ = df[df['line'].isin(lines)].reset_index(drop=True)

    if time_type == 'days':
        df__ = df_[df_['day_value'].isin(d)][['day_value', 'hour', 'line',
                                              'number_of_passenger', 'number_of_passage']].reset_index(drop=True)
        df_grouped = df__.groupby(['day_value', 'hour', 'line']).mean().reset_index().round(2) \
            .rename(columns={'number_of_passenger': 'avg_number_of_passenger',
                             'number_of_passage': 'avg_number_of_passage'})
        return df_grouped
    else:
        df__ = df_[df_['hour'].isin(h)][['hour', 'line',
                                         'number_of_passenger', 'number_of_passage']].reset_index(drop=True)
        df_grouped = df__.groupby(['hour', 'line']).mean().reset_index().round(2) \
            .rename(columns={'number_of_passenger': 'avg_number_of_passenger',
                             'number_of_passage': 'avg_number_of_passage'})
        return df_grouped


def transform(d):
    return {value: key for key, value in d.items()}


def creating_line_graph_based_date(time_type, df_2020, df_2021, col, m=1):
    """
    :param time_type: string
    :param df_2020: dataframe
    :param df_2021: dataframe
    :param col: string
    :param m: int
    :return: Plotly Line Graph
    """
    if col == 'avg_number_of_passenger':
        title_ = 'Average Passenger Count by Given Time Type'
        yxs = 'Avg Passenger Count'
    else:
        title_ = 'Average Passage Count by based on Given Time Type'
        yxs = 'Avg Passage Count'

    if time_type == 'days':
        xaxis_title_ = 'Day(s) & Hours'
        xaxis_ = dict()
    else:
        xaxis_title_ = 'Hours'
        xaxis_ = dict(tickmode='linear', tick0=1)

    reverse_months = [{value: key for key, value in config.months.items()}][0]
    nm_month = reverse_months[m]

    order_list_20 = df_2020['date'].unique().tolist()
    order_list_21 = df_2021['date'].unique().tolist()
    df_2020_pv = pd.pivot_table(df_2020, values=col, index=['date'],
                                columns='line', aggfunc=np.sum).reindex(order_list_20)
    df_2021_pv = pd.pivot_table(df_2021, values=col, index=['date'],
                                columns='line', aggfunc=np.sum).reindex(order_list_21)

    fig_20 = go.Figure()
    for c in df_2020_pv.columns:
        fig_20.add_trace(go.Scatter(x=df_2020_pv.index, y=df_2020_pv[c].values,
                                    name=c + ' // {0} 2020'.format(nm_month),
                                    mode='lines',
                                    line=dict(shape='linear'),
                                    connectgaps=True,
                                    showlegend=True
                                    )
                         )

    fig_21 = go.Figure()
    for c in df_2021_pv.columns:
        fig_21.add_trace(go.Scatter(x=df_2021_pv.index, y=df_2021_pv[c].values,
                                    name=c + ' // {0} 2021'.format(nm_month),
                                    mode='lines',
                                    line=dict(shape='linear'),
                                    connectgaps=True,
                                    showlegend=True
                                    )
                         )

    fig_20.update_layout(
        title=title_,
        xaxis=xaxis_,
        xaxis_title=xaxis_title_,
        yaxis_title=yxs,
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        )
    )

    fig_21.update_layout(
        title=title_,
        xaxis=xaxis_,
        xaxis_title=xaxis_title_,
        yaxis_title=yxs,
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        )
    )

    return fig_20.show(), fig_21.show()


def creating_line_graph_for_single_line(time_type, df_2020, df_2021, col, sline, m=1):
    if col == 'avg_number_of_passenger':
        title_ = 'Average Passenger Count by Given Time Type'
        yxs = 'Avg Passenger Count'
    else:
        title_ = 'Average Passage Count by based on Given Time Type'
        yxs = 'Avg Passage Count'

    if time_type == 'days':
        xaxis_title_ = 'Day(s) & Hours'
        xaxis_ = dict()
    else:
        xaxis_title_ = 'Hours'
        xaxis_ = dict(tickmode='linear', tick0=1)

    reverse_months = [{value: key for key, value in config.months.items()}][0]
    nm_month = reverse_months[m]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_2020['hour'], y=df_2020[col],
                             line=dict(color='royalblue'),
                             showlegend=True, name='{0}'.format(sline) + ' // {0} 2020'.format(nm_month),
                             mode='lines'))
    fig.add_trace(go.Scatter(x=df_2021['hour'], y=df_2021[col],
                             line=dict(color='firebrick'),
                             showlegend=True, name='{0}'.format(sline) + ' // {0} 2021'.format(nm_month),
                             mode='lines'))

    fig.update_layout(
        title=title_,
        xaxis=xaxis_,
        xaxis_title=xaxis_title_,
        yaxis_title=yxs,
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        )
    )
    return fig.show()


def main():
    df = data_preparation()

    # The localhost page is opened on the Internet browser.
    # Each plot is presented in a separate browser tab.
    # graph part I
    for m in config.pth_months:
        df_20 = data_generator(data=df, year=2020, month=m)
        df_21 = data_generator(data=df, year=2021, month=m)
        for col in config.pth_cols:
            m_ = [config.months[key] for key in config.months if key == m][0]
            creating_line_graph_based_day(creating_daily_data(df_20.copy()),
                                          creating_daily_data(df_21.copy()),
                                          col=col, m=m_)
            creating_line_graph_based_day(creating_day_avg_data(df_20.copy()),
                                          creating_day_avg_data(df_21.copy()),
                                          col='avg_' + col, m=m_)
    # graph part II
    for col in config.pth_cols:
        creating_bar_graph_based_transport_type(dat=df.copy(), col=col)

    # graph part III
    for col in config.pth_cols:
        for t in config.pth_types:
            creating_bar_graph_based_transport_type_in_details(dat=df.copy(), value_type=col, type_desc=t)

    # graph part IV
    for m in config.pth_months:
        df_20 = data_generator(data=df.copy(), year=2020, month=m, is_line=True)
        df_21 = data_generator(data=df.copy(), year=2021, month=m, is_line=True)
        m_ = [config.months[key] for key in config.months if key == m][0]
        for c in config.pth_cols:
            col_ = 'avg_' + c

            # Day - Hour
            dh_20 = creating_avg_data_all_date_breakdown(df=df_20.copy(), lines=config.pth_lines, time_type='days',
                                                         d=config.pth_days)
            dh_20['date'] = dh_20.apply(lambda row: row['day_value'] + ' - Hour ' + str(row['hour']), axis=1)
            dh_21 = creating_avg_data_all_date_breakdown(df=df_21.copy(), lines=config.pth_lines, time_type='days',
                                                         d=config.pth_days)
            dh_21['date'] = dh_21.apply(lambda row: row['day_value'] + ' - Hour ' + str(row['hour']), axis=1)
            creating_line_graph_based_date(time_type='days', df_2020=dh_20.copy(), df_2021=dh_21.copy(), col=col_,
                                           m=m_)

            # Hour
            h_20 = creating_avg_data_all_date_breakdown(df=df_20.copy(), lines=config.pth_lines, time_type='hours',
                                                        h=config.pth_hours)
            h_21 = creating_avg_data_all_date_breakdown(df=df_21.copy(), lines=config.pth_lines, time_type='hours',
                                                        h=config.pth_hours)
            creating_line_graph_based_date(time_type='hours', df_2020=h_20.copy().rename(columns={'hour': 'date'}),
                                           df_2021=h_21.copy().rename(columns={'hour': 'date'}), col=col_, m=m_)

            # Single line - All hours
            h_20 = creating_avg_data_all_date_breakdown(df=df_20.copy(), lines=config.pth_lines_single,
                                                        time_type='hours', h=config.hours)
            h_21 = creating_avg_data_all_date_breakdown(df=df_21.copy(), lines=config.pth_lines_single,
                                                        time_type='hours', h=config.hours)
            creating_line_graph_for_single_line(time_type='hours', df_2020=h_20.copy(), df_2021=h_21.copy(),
                                                col=col_, sline=config.pth_lines_single, m=m_)


if __name__ == "__main__":
    main()

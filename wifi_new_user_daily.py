#!/usr/bin/python3
# -*- coding: utf-8 -*-

import config
import datapane as dp
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
import utils

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('IMM Data Visualization - Daily Wifi New User')


def data_preparation():
    """
    :return: dataframe
    """
    # getting data
    data = utils.getting_raw_data(dat_name='wnu')
    data.columns = ['subscription_date', 'subscription_county', 'subscription_type', 'lon', 'lat',
                    'number_of_subscription']
    # converting from Turkish to English for subscription type column
    data['subscription_type'] = data['subscription_type'].map({'Yerli': 'domestic',
                                                               'Yabancı': 'foreign',
                                                               'Bilinmiyor': 'unknown'})
    # Changing data type for date column, str -> timestamp
    data['subscription_date'] = pd.to_datetime(data['subscription_date'])
    return data


def creating_line_graph_based_date(df, date_type):
    """
    :param df: dataframe
    :param date_type: string
    :return: Plotly Scatter Plot
    """
    if date_type == 'daily':
        title_ = 'Daily Subscription Count'
        mode_ = 'lines'
    else:
        df['subscription_date'] = df['subscription_date'].dt.strftime('%Y-%m')
        title_ = 'Monthly Subscription Count'
        mode_ = 'lines+markers'

    df_grouped = df[['subscription_date', 'number_of_subscription']].groupby('subscription_date').sum().reset_index()

    fig = go.Figure(data=go.Scatter(x=df_grouped['subscription_date'], y=df_grouped['number_of_subscription'],
                                    marker_color=df_grouped['number_of_subscription'], showlegend=True,
                                    name="Number of Subscription", mode=mode_))
    fig.update_layout(
        title=title_,
        xaxis_title='Date',
        yaxis_title='Subscription Count',
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        ),
        width=900,
        height=650
    )
    return fig


def creating_bar_graph(df, col):
    """
    :param df: dataframe
    :param col: string
    :return: Plotly Express Bar Plot
    """
    if col == 'subscription_county':
        xlbl = 'County'
        rtt = 90
    else:
        xlbl = 'Type'
        rtt = 0

    df_grouped = df[[col, 'number_of_subscription']].groupby(col).sum().reset_index()
    fig = px.bar(df_grouped, x=col, y='number_of_subscription', color=col, height=600)
    fig.update_layout(
        title='Subscription Count by {0}'.format(xlbl),
        xaxis=dict(
            tickangle=rtt
        ),
        xaxis_title=xlbl,
        yaxis_title='Subscription Count',
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        ),
        showlegend=False,
        width=900,
        height=650
    )
    return fig


def creating_stack_bar_graph(dat):
    """
    :param dat: dataframe
    :return: Plotly Express Bar Plot
    """
    dat_county_ = dat[dat['subscription_county'].isin(config.wnu_county_list_)][
        ['subscription_county', 'subscription_type', 'number_of_subscription']]
    df_stack = dat_county_.groupby(['subscription_county', 'subscription_type']).size().reset_index()
    df_stack['percentage'] = dat_county_.groupby(['subscription_county', 'subscription_type'])\
        .size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    df_stack.rename(columns={0: 'number_of_subscription'}, inplace=True)
    df_stack['percentage'] = df_stack['percentage'].map('{:,.2f}%'.format)

    fig = px.bar(df_stack, x='subscription_county', y='number_of_subscription', color='subscription_type',
                 barmode='stack', text=df_stack['percentage'])

    fig.update_layout(title="Subscription Count by County & Type", xaxis_title='County',
                      yaxis_title='Subscription Count', width=900, height=650)

    return fig


def main():
    """
    :return: Plotly Figure
    """
    df = data_preparation()

    # The localhost page is opened on the Internet browser.
    # Each plot is presented in a separate browser tab.
    for dt in config.date_type:
        creating_line_graph_based_date(df=df, date_type=dt)
    for c in ['subscription_county', 'subscription_type']:
        creating_bar_graph(df=df, col=c)
    creating_stack_bar_graph(dat=df)


def putting_into_streamlit():
    """
    :return: None
    """
    df = data_preparation()
    st.markdown("## **:signal_strength: Daily IMM WiFi New User Data Visualization**")

    for dt in config.date_type:
        st.write(creating_line_graph_based_date(df=df, date_type=dt))

    for c in ['subscription_county', 'subscription_type']:
        st.write(creating_bar_graph(df=df, col=c))

    st.write(creating_stack_bar_graph(dat=df))


def putting_into_datapane():
    """
    :return: None
    """
    # getting token
    dp.login(config.dp_token)
    # getting data
    df = data_preparation()
    # line graph
    p1 = creating_line_graph_based_date(df=df, date_type='monthly')
    dp.Report(dp.Plot(p1)).publish(name='Monthly Subscription Count', open=True)
    # bar graph
    p2 = creating_bar_graph(df=df, col='subscription_county')
    dp.Report(dp.Plot(p2)).publish(name='Subscription Count by County', open=True)
    # stack bar graph
    p3 = creating_stack_bar_graph(dat=df)
    dp.Report(dp.Plot(p3)).publish(name='Subscription Count by County & Type', open=True)

    dp.logout()


if __name__ == "__main__":
    # main()
    putting_into_streamlit()
    # putting_into_datapane()


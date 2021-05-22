#!/usr/bin/python3
# -*- coding: utf-8 -*-

import config
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
import utils

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('IMM Data Visualization - Dam Occupancy Rates')


def data_preparation():
    """
    :rtype: dataframe
    """
    # getting data
    data = utils.getting_raw_data(dat_name='dor')
    data.columns = ['date', 'occupancy_rate', 'reserved_water']

    # Changing data type for date column, str -> timestamp
    data['date'] = pd.to_datetime(data['date'])

    return data


def creating_line_graph_based_date(df, date_type, col):
    """
    :param df: dataframe
    :param date_type:
    :param col:
    :return: Plotly Line Graph
    """
    if date_type == 'daily':
        if col == 'occupancy_rate':
            title_ = 'Daily General Dam Occupancy Rate'
            yxs = 'Occupancy Rate'
            nm = 'Dam Occupancy Rate'
        else:
            title_ = 'Daily General Dam Reserved Water'
            yxs = 'Reserved Water'
            nm = 'Dam Reserved Water'
        mode_ = 'lines'

    else:
        if col == 'occupancy_rate':
            title_ = 'Monthly General Dam Occupancy Rate'
            yxs = 'Average Occupancy Rate'
            nm = 'Dam Occupancy Rate'
        else:
            title_ = 'Monthly General Dam Reserved Water'
            yxs = 'Total Reserved Water'
            nm = 'Dam Reserved Water'
        df['date'] = df['date'].dt.strftime('%Y-%m')
        mode_ = 'lines+markers'

    if col == 'occupancy_rate':
        df_grouped = df[['date', col]].groupby('date').mean().reset_index()
        df_grouped[col] = round(df_grouped[col], 2)
    else:
        df_grouped = df[['date', col]].groupby('date').sum().reset_index()

    fig = go.Figure(data=go.Scatter(x=df_grouped['date'], y=df_grouped[col], showlegend=True, name=nm, mode=mode_,
                                    marker={'color': ["red"] * len(df_grouped)}))
    fig.update_layout(
        title=title_,
        xaxis_title='Date',
        yaxis_title=yxs,
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        ),
        width=900,
        height=650
    )
    return fig


def classify(e):
    """
    :param e: float
    :rtype: string
    """
    if e > 0.75:
        return 'high'
    if e > 0.25:
        return 'medium'
    if e >= 0:
        return 'low'


def modes(df):
    """
    :param df: dataframe
    :rtype: string
    """
    if len(df) > 1:
        return 'lines'
    else:
        return 'markers'


def creating_colorful_line_graph_based_date(df, col):
    """
    :param df: dataframe
    :param col: string
    :return: Plotly Line Graph
    """
    # getting raw data
    df_ = df[['date', col]].rename(columns={'date': 'time', col: 'value'})
    df_fig = df_.copy().set_index('time')

    # creating figure data
    df_['label_'] = [(elem - df_['value'].min()) / (df_['value'].max() - df_['value'].min()) for elem in df_['value']]
    df_['label'] = [classify(elem) for elem in df_['label_']]
    df_ = df_.drop('label_', 1)
    df_['group'] = df_['label'].ne(df_['label'].shift()).cumsum()
    df_ = df_.groupby('group')
    dfs = []
    for name, data in df_:
        dfs.append(data)

    if col == 'occupancy_rate':
        title_ = 'Daily General Dam Occupancy Rate'
        yxs = 'Occupancy Rate'
        nm = 'Dam Occupancy Rate'
    else:
        title_ = 'Daily General Dam Reserved Water'
        yxs = 'Reserved Water'
        nm = 'Dam Reserved Water'

    # vis
    fig = go.Figure((go.Scatter(x=df_fig.index, y=df_fig['value'], name=nm, line=dict(color='rgba(200,200,200,0.7)'))))
    cols = {'high': 'green', 'medium': 'blue', 'low': 'red'}

    showed = []
    for frame in dfs:
        if frame['label'].iloc[0] not in showed:
            fig.add_trace(go.Scatter(x=frame['time'], y=frame['value'], mode=modes(frame),
                                     marker_color=cols[frame['label'].iloc[0]], legendgroup=frame['label'].iloc[0],
                                     name=frame['label'].iloc[0]))
            showed.append(frame['label'].iloc[0])
        else:
            fig.add_trace(go.Scatter(x=frame['time'], y=frame['value'], mode=modes(frame),
                                     marker_color=cols[frame['label'].iloc[0]], legendgroup=frame['label'].iloc[0],
                                     name=frame['label'].iloc[0], showlegend=False))

    fig.update_layout(
        template='plotly_dark',
        title=title_,
        xaxis_title='Date',
        yaxis_title=yxs,
        font=dict(
            family='Verdana',
            size=10,
            color='white'
        ),
        width=900,
        height=650
    )
    fig.update_xaxes(showgrid=False)
    fig.update_layout(uirevision='constant')
    return fig


def creating_bar_graph_for_occupancy(df, month='all'):
    """
    :param df: dataframe
    :param month: string
    :return: Plotly Bar Graph
    """
    df['year'] = df['date'].apply(lambda row: row.year)
    df['month'] = df['date'].apply(lambda row: row.month_name())
    df_pre = df[['year', 'month', 'occupancy_rate']]\
        .groupby(['year', 'month']).mean().reset_index()\
        .rename(columns={'occupancy_rate': 'avg_occupancy_rate'})

    if month != 'all':
        df_ = df_pre[df_pre['month'] == month].reset_index(drop=True)
        x_ = 'year'
        xaxis_title_ = 'Year'
        title_ = 'Comparison of Avg Occupancy Rate based on Year [only {0}]'.format(month)
    else:
        df_1 = df_pre[df_pre['year'] != 2021].reset_index(drop=True)
        del df_1['year']
        df_2 = df_1.groupby('month').mean().reset_index()
        df_ = df_2.set_index('month').reindex([key for key in config.months]).reset_index()
        x_ = 'month'
        xaxis_title_ = 'Month'
        title_ = 'Comparison of Avg Occupancy Rate based on Months [2005 - 2021)'

    df_['avg_occupancy_rate'] = round(df_['avg_occupancy_rate'], 4)

    # vis
    fig = px.bar(df_, x=x_, y='avg_occupancy_rate', color='avg_occupancy_rate',
                 labels={'avg_occupancy_rate': 'Avg Occupancy Rate'}, color_continuous_scale=px.colors.sequential.Jet,
                 opacity=0.60)

    fig.update_layout(
        title=title_,
        xaxis=dict(
            tickangle=0,
            dtick=1
        ),
        xaxis_title=xaxis_title_,
        yaxis_title='Avg Occupancy Rate',
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
    for dt in config.date_type:
        for col in config.dor_cols:
            creating_line_graph_based_date(df=df.copy(), date_type=dt, col=col)

    for c in config.dor_cols:
        creating_colorful_line_graph_based_date(df=df.copy(), col=c)

    for m in config.dor_months:
        creating_bar_graph_for_occupancy(df=df.copy(), month=m)
    creating_bar_graph_for_occupancy(df=df.copy())


def putting_into_streamlit():
    """
    :return: None
    """
    df = data_preparation()
    st.markdown("## **:ocean: Istanbul Dam Occupancy Rates Visualization**")

    for dt in config.date_type:
        for col in config.dor_cols:
            st.write(creating_line_graph_based_date(df=df.copy(), date_type=dt, col=col))

    # if it will be run this code block, please use the dark theme in streamlit
    # for c in config.dor_cols:
    #     st.write(creating_colorful_line_graph_based_date(df=df.copy(), col=c))

    for m in config.dor_months:
        st.write(creating_bar_graph_for_occupancy(df=df.copy(), month=m))

    st.write(creating_bar_graph_for_occupancy(df=df.copy()))


def putting_into_datapane():
    return


if __name__ == "__main__":
    # main()
    putting_into_streamlit()

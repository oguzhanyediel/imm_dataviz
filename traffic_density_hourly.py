#!/usr/bin/python3
# -*- coding: utf-8 -*-

import config
import logging
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
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
        yaxis_title='Day',
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        )
    )

    return fig.show()


def creating_annotated_heatmap(df, year, month, annotation_type, htype='day', is_rush_hour=False,
                               rush_hour_type='Morning'):
    """
    :param df: dataframe
    :param year: int
    :param month: string
    :param annotation_type: string; Number or Percentage
    :param htype: string; day or hour
    :param is_rush_hour: bool
    :param rush_hour_type: string; Morning or Evening
    :return: Plotly Annotated Heatmap Graph
    """
    if is_rush_hour is True:
        df_pre = df[(df['year'] == year) & (df['month'] == month)].reset_index(drop=True)
        if rush_hour_type == 'Evening':
            df_ = df_pre[df_pre['hour'].isin(config.tdh_evening_rush_hours)].reset_index(drop=True)
        else:
            df_ = df_pre[df_pre['hour'].isin(config.tdh_morning_rush_hours)].reset_index(drop=True)
    else:
        df_ = df[(df['year'] == year) & (df['month'] == month)].reset_index(drop=True)

    days_ = config.days[::-1]
    axis_ = 'columns'

    if annotation_type == 'Number':
        # title
        title_ = 'Traffic Density Heatmap by Day & Hour [{0} - {1}]'.format(month, year)
        cb_title = 'Avg Number of Vehicles'

        # grouping
        df_grouped = df_[['day', 'hour', 'number_of_vehicles']] \
            .groupby(['day', 'hour']).mean().reset_index() \
            .rename(columns={'number_of_vehicles': 'avg_number_of_vehicles'})
        df_grouped['avg_number_of_vehicles'] = round(df_grouped['avg_number_of_vehicles'], 2)
        # creating pivot data
        df_pivot = pd.pivot_table(data=df_grouped, values='avg_number_of_vehicles', index='hour', columns='day')
    else:  # Percentage
        cb_title = '[Pct] Avg Number of Vehicles'

        if htype == 'hour':
            axis_ = 'index'
            days_ = config.days
            # title
            title_ = 'Traffic Density Heatmap // Percentage by Hour [{0} - {1}]'.format(month, year)

            # grouping
            dfg = df_[['hour', 'day', 'number_of_vehicles']] \
                .groupby(['hour', 'day']) \
                .agg({'number_of_vehicles': 'mean'}) \
                .rename(columns={'number_of_vehicles': 'avg_number_of_vehicles'})
            df_grouped = dfg.groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).reset_index()
            df_grouped['avg_number_of_vehicles'] = round(df_grouped['avg_number_of_vehicles'], 2)

            # creating pivot data
            df_pivot = pd.pivot_table(data=df_grouped, values='avg_number_of_vehicles', index='day', columns='hour')
        else:
            title_ = 'Traffic Density Heatmap // Percentage by Day [{0} - {1}]'.format(month, year)

            # grouping
            df_grouped = pd.DataFrame()
            for d in days_:
                dfg = df_[df_['day'] == d][['day', 'hour', 'number_of_vehicles']] \
                    .groupby(['day', 'hour']) \
                    .agg({'number_of_vehicles': 'mean'}) \
                    .rename(columns={'number_of_vehicles': 'avg_number_of_vehicles'})
                dfg_ = dfg.groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).reset_index()
                dfg_['avg_number_of_vehicles'] = round(dfg_['avg_number_of_vehicles'], 2)
                df_grouped = df_grouped.append(dfg_)

            # creating pivot data
            df_pivot = pd.pivot_table(data=df_grouped, values='avg_number_of_vehicles', index='hour', columns='day')

    # vis
    ff_fig = ff.create_annotated_heatmap(z=df_to_plotly_heatmap_data(df_pivot.reindex(days_, axis=axis_))['z'],
                                         x=df_to_plotly_heatmap_data(df_pivot.reindex(days_, axis=axis_))['x'],
                                         y=df_to_plotly_heatmap_data(df_pivot.reindex(days_, axis=axis_))['y'],
                                         showscale=True, colorbar=dict(title=cb_title))
    fig = go.FigureWidget(ff_fig)

    # arrangements
    if htype == 'hour':
        xaxis_title = 'Hour'
        yaxis_title = 'Day'
    else:
        xaxis_title = 'Day'
        yaxis_title = 'Hour'

    fig.update_layout(
        title=title_,
        xaxis=dict(
            title=xaxis_title,
            dtick=1,
            side='bottom'
        ),
        yaxis=dict(
            title=yaxis_title,
            dtick=1

        ),
        font=dict(
            family='Verdana',
            size=10,
            color='black'
        )
    )
    return fig.show()


def creating_density_mapbox(dat, year, month):
    """
    :param dat: dataframe
    :param year: int
    :param month: string
    :return: Plotly Density Mapbox
    """
    # data preparation
    data = dat[['date_time', 'longitude', 'latitude', 'number_of_vehicles']]
    data['year'] = data['date_time'].apply(lambda row: row.year)
    data['month'] = data['date_time'].apply(lambda row: row.month_name())

    # data selection
    df = data[(data['year'] == year) & (data['month'] == month)][
        ['latitude', 'longitude', 'number_of_vehicles']].reset_index(drop=True)
    df_ = df.groupby(['latitude', 'longitude']).mean().reset_index().rename(
        columns={'number_of_vehicles': 'avg_number_of_vehicles'})
    df_['avg_number_of_vehicles'] = round(df_['avg_number_of_vehicles'], 2)

    # vis
    fig = px.density_mapbox(df_, lat='latitude', lon='longitude', z='avg_number_of_vehicles',
                            radius=13, zoom=8.12, height=650, center=dict(lat=41.10, lon=28.70),
                            mapbox_style="carto-positron",
                            title='Density Map of Average Vehicle Count by Month [{0} - {1}]'.format(month, year),
                            labels={'avg_number_of_vehicles': 'Avg Number of Vehicle'},
                            hover_data={'latitude': False, 'longitude': False, 'avg_number_of_vehicles': True})
    fig.show()


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
            creating_annotated_heatmap(df=data.copy(), year=y, month=m, annotation_type='Number')
            # creating_annotated_heatmap(df=data.copy(), year=y, month=m, annotation_type='Number', is_rush_hour=True)
            # creating_annotated_heatmap(df=data.copy(), year=y, month=m, annotation_type='Number', is_rush_hour=True,
            #                            rush_hour_type='Evening')
            creating_annotated_heatmap(df=data.copy(), year=y, month=m, annotation_type='Percentage')
            creating_annotated_heatmap(df=data.copy(), year=y, month=m, annotation_type='Percentage', htype='hour')
            creating_density_mapbox(dat=df, year=y, month=m)


def putting_into_datapane():
    return


def putting_into_streamlit():
    return


if __name__ == "__main__":
    main()

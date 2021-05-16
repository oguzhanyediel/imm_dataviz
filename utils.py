#!/usr/bin/python3
# -*- coding: utf-8 -*-

import config
import io
import logging
import pandas as pd
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('IMM Data Visualization - Util Functions')


def getting_raw_data(dat_name, url_list=False):
    """
    :param dat_name: string
    :param url_list: bool
    :rtype: dataframe
    """
    # The data were taken automatically by using the URL instead of downloading manually because it is updated.
    # Footnote: The data are generally 45 days behind and are updated daily.
    if url_list is True:
        if dat_name == 'pth':
            url_list = config.public_transport_data_url_list
        else:
            url_list = config.traffic_density_data_url_list

        dat = pd.DataFrame()
        for u in url_list:
            s = requests.get(u).content
            dat = dat.append(pd.read_csv(io.StringIO(s.decode('utf-8'))))
        return dat

    if dat_name == 'dor':
        url = config.dam_occ_rates_data_url
    elif dat_name == 'wnu':
        url = config.wifi_new_user_data_url
    else:
        url = config.traffic_announcements_url

    s = requests.get(url).content
    return pd.read_csv(io.StringIO(s.decode('utf-8')))


#!/usr/bin/python3
# -*- coding: utf-8 -*-

# IMM Data Visualization Project - Configuration File

# This configuration file can contain the necessary information of the project,
# such as database connections credentials, some important variables, etc.

dam_occ_rates_data_url = 'https://data.ibb.gov.tr/en/dataset/19c14482-14f2-4803-b4df-4cf4c6c42016/resource/b68cbdb0-9bf5-474c-91c4-9256c07c4bdf/download/dam_occupancy.csv'
public_transport_data_url_list = [
    'https://data.ibb.gov.tr/en/dataset/a6855ce7-4092-40a5-82b5-34cf3c7e36e3/resource/511c5034-0a1c-4c77-9831-157f30e62aee/download/hourly_transportation_202001.csv',
    'https://data.ibb.gov.tr/en/dataset/a6855ce7-4092-40a5-82b5-34cf3c7e36e3/resource/de831d1d-85a3-478e-8167-72223ee7ffaa/download/hourly_transportation_202002.csv',
    'https://data.ibb.gov.tr/en/dataset/a6855ce7-4092-40a5-82b5-34cf3c7e36e3/resource/004994f5-3a50-4721-8787-41d4940bdaee/download/hourly_transportation_202101.csv',
    'https://data.ibb.gov.tr/en/dataset/a6855ce7-4092-40a5-82b5-34cf3c7e36e3/resource/a22578e4-3c72-454b-a9e4-d843b7e649e8/download/hourly_transportation_202102.csv']
traffic_density_data_url_list = [
    'https://data.ibb.gov.tr/en/dataset/3ee6d744-5da2-40c8-9cd6-0e3e41f1928f/resource/db9c7fb3-e7f9-435a-92f4-1b917e357821/download/traffic_density_202001.csv',
    'https://data.ibb.gov.tr/en/dataset/3ee6d744-5da2-40c8-9cd6-0e3e41f1928f/resource/5fb30ee1-e079-4865-a8cd-16efe2be8352/download/traffic_density_202002.csv',
    'https://data.ibb.gov.tr/en/dataset/3ee6d744-5da2-40c8-9cd6-0e3e41f1928f/resource/fb7094a3-cf2f-46a6-996a-f6a9c5f3b9be/download/traffic_density_202101.csv',
    'https://data.ibb.gov.tr/en/dataset/3ee6d744-5da2-40c8-9cd6-0e3e41f1928f/resource/395811ac-4152-4e04-88ef-8d4e30e6ac17/download/traffic_density_202102.csv']
wifi_new_user_data_url = 'https://data.ibb.gov.tr/en/dataset/015e8185-d59c-47c1-a4cf-8d7fc709ef44/resource/12f5bc23-224a-43cb-b60d-3f36f83ffd33/download/ibb_wifi_subscriber.csv'
traffic_announcements_url = 'https://data.ibb.gov.tr/en/dataset/8d47d214-eca8-494d-9457-d134dde561ff/resource/1c043914-8a76-4793-bae9-c60a68c7d389/download/traffic_announcement.csv'

# some variables that are easily changeable
wnu_county_list_ = ['BAKIRKÖY', 'EYÜP SULTAN', 'FATİH', 'KADIKÖY', 'KARTAL', 'MALTEPE']
date_type = ['daily', 'monthly']
dor_cols = ['occupancy_rate', 'reserved_water']
dor_months = ['October', 'December', 'July']
pth_cols = ['number_of_passenger', 'number_of_passage']
pth_months = ['January', 'February']
pth_years = [2020, 2021]
pth_types = ['Highway', 'Rail', 'Sea']
pth_lines = ['AKSARAY-HAVALİMANI', 'KABATAŞ-BAĞCILAR', 'MARMARAY', 'TAKSİM-4.LEVENT']
pth_lines_single = 'METROBÜS'
pth_days = ['Monday', 'Tuesday']
pth_hours = [7, 8, 9, 10]
hours = [i for i in range(0, 24)]
months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
          'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
days = ['Sunday', 'Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday']
tdh_years = [2020, 2021]
tdh_months = ['January', 'February']
tdh_evening_rush_hours = [18, 19, 20]
tdh_morning_rush_hours = [6, 7, 8, 9]

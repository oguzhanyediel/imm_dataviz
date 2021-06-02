#!/bin/bash

set -e

exec streamlit run wifi_new_user_daily.py --server.port 8502 &
exec streamlit run dam_occupancy_rates_daily.py --server.port 8503 &
exec streamlit run public_transport_hourly.py --server.port 8504 &
exec streamlit run traffic_density_hourly.py --server.port 8505 &
exec streamlit run traffic_announcements_instant.py --server.port 8506
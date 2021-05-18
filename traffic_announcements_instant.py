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


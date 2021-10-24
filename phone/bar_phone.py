import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

import pandas as pd
import numpy as np
from dash.dependencies import Output, Input


data = pd.read_csv("20191226-items.csv")
data = data.query("brand == 'Motorola' or brand == 'Nokia'or brand == 'Samsung' or brand == 'Sony' or brand == 'Apple' or brand == 'Xiaomi' or brand == 'HUAWEI' or brand == 'OnePlus' or brand == 'Google' or brand == 'ASUS'")
data.sort_values("title", inplace=True)



fig = px.bar(data, x = 'title', y = 'rating')
fig.show()

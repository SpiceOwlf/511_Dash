# $ python3 -m venv venv
# $ source venv/bin/activate
# $ python -m pip install dash==1.13.3 pandas==1.0.5
# python3 dot_phone.py
# https://stackabuse.com/plotly-bar-plot-tutorial-and-examples/

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

import pandas as pd
import numpy as np
from dash.dependencies import Output, Input


# asin,brand,title,url,image,rating,reviewUrl,totalReviews,price,originalPrice

data = pd.read_csv("20191226-items.csv")
data = data.query("brand == 'Motorola' or brand == 'Nokia'or brand == 'Samsung' or brand == 'Sony' or brand == 'Apple' or brand == 'Xiaomi' or brand == 'HUAWEI' or brand == 'OnePlus' or brand == 'Google' or brand == 'ASUS'")
data.sort_values("title", inplace=True)
df = data


fig = px.scatter(df, x="rating", y="price", color="brand",
                 title="rating-price relationship with brand",
                 labels={"brand":"brand"} 
                )
fig.show()

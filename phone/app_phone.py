# $ python3 -m venv venv
# $ source venv/bin/activate
# $ python -m pip install dash==1.13.3 pandas==1.0.5
# python app.py
# http://localhost:8050


import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input


# asin,brand,title,url,image,rating,reviewUrl,totalReviews,price,originalPrice

data = pd.read_csv("20191226-items.csv")
data.sort_values("title", inplace=True)

external_stylesheets = [
    {
        "href": "assets/style.css",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "phone data"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="phone_demo01", className="header-emoji"),
                html.H1(
                    children="Phone Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze the behavior of phone prices, title and rates"
                    " and the number of phones sold in the US",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart",
                        config={"displayModeBar": False},
                        figure={
                            "data": [
                                {
                                    "x": data["title"],
                                    "y": data["price"],
                                    "type": "lines",
                                    "hovertemplate": "$%{y:.2f}"
                                                     "<extra></extra>",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "Price of Phones based on title",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True},
                                "yaxis": {
                                    "tickprefix": "$",
                                    "fixedrange": True,
                                },
                                "colorway": ["#17B897"],
                            },
                        },
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volume-chart",
                        config={"displayModeBar": False},
                        figure={
                            "data": [
                                {
                                    "x": data["title"],
                                    "y": data["rating"],
                                    "type": "lines",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "Phone Rating",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True},
                                "yaxis": {"fixedrange": True},
                                "colorway": ["#E12D39"],
                            },
                        },
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)



if __name__ == "__main__":
    app.run_server(debug=True)
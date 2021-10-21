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
data = data.query("brand == 'Motorola' or brand == 'Nokia'or brand == 'Samsung' or brand == 'Sony' or brand == 'Apple' or brand == 'Xiaomi' or brand == 'HUAWEI' or brand == 'OnePlus' or brand == 'Google' or brand == 'ASUS'")
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
                    children=[
                        html.Div(children="Brand", className="menu-title"),
                        dcc.Dropdown(
                            id="brand-filter",
                            options=[
                                {"label": brand, "value": brand}
                                for brand in np.sort(data.brand.unique())
                            ],
                            value="Nokia",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="rating Range",
                            className="menu-title"
                            ),
                        dcc.RangeSlider(
                            id="rating-range",
                            min=data.rating.min(),
                            max=data.rating.max(),
                            step = 0.5,
                            value=[0,5],
                            marks={
                                1:'1',
                                2:'2',
                                3:'3',
                                4:'4',
                                5:'5',
                                6:'6',
                            }
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="price Range",
                            className="menu-title"
                            ),
                        dcc.RangeSlider(
                            id="price-range",
                            min=data.price.min(),
                            max=data.price.max(),
                            step = 1,
                            value=[0,100],
                            marks={
                                1:'1',
                                100:'100',
                                500:'500',
                                900:'900',
                            },
                            allowCross=False
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        



       html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volume-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    [Output("price-chart", "figure"), Output("volume-chart", "figure")],
    [
        Input("brand-filter", "value"),
        Input("rating-range","value"),
        Input("price-range","value"),
    ],
)

def update_charts(brand,rating_slider, price_slider):
    mask = (
        (data.brand == brand)
        &(data.rating >= rating_slider[0])
        &(data.rating <= rating_slider[1])
        &(data.price >= price_slider[0])
        &(data.price <= price_slider[1])
    )
    filtered_data = data.loc[mask, :]
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["title"],
                "y": filtered_data["price"],
                "type": "lines",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Average Price of brand",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data["title"],
                "y": filtered_data["rating"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "rating of brand", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)
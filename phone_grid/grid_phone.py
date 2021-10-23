# $ python3 -m venv venv
# $ source venv/bin/activate
# $ python -m pip install dash==1.13.3 pandas==1.0.5
# python3 grid_phone.py
# http://localhost:8050
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


df = pd.read_csv("20191226-items.csv")
df = df.query("brand == 'Motorola' or brand == 'Nokia'or brand == 'Samsung' or brand == 'Sony' or brand == 'Apple' or brand == 'Xiaomi' or brand == 'HUAWEI' or brand == 'OnePlus' or brand == 'Google' or brand == 'ASUS'")
df.sort_values("title", inplace=True)

app = dash.Dash(__name__)


app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 50,
    ),
    html.Div(id='datatable-interactivity-container')
])





if __name__ == "__main__":
    app.run_server(debug=True)
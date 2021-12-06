import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from data_model import ColumnBasedModel

df = pd.read_csv("20191226-items.csv")
df = df.query("brand == 'Motorola' or brand == 'Nokia'or brand == 'Samsung' or brand == 'Sony' or brand == 'Apple' or brand == 'Xiaomi' or brand == 'HUAWEI' or brand == 'OnePlus' or brand == 'Google' or brand == 'ASUS'")
df.sort_values("title", inplace=True)

data = ColumnBasedModel(list(df.to_dict('records')[0].keys()), df.to_dict('records'))

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(id='datatable-interactivity-container'),
    html.Div(id='datatable-update-container'),
    html.Button('Delete', id='delete', n_clicks=0),
    html.Button('Display Selected Columns', id='display-selected-column', n_clicks=0),
    html.Button('Revert Last Action', id='revert-action', n_clicks=0),
    html.Button('Revert All Actions', id='revert-all-action', n_clicks=0),
    html.Button('Save Changes to Database', id='save-to-database', n_clicks=0),
    html.Div(id='save-to-database-container'),
    dash_table.DataTable(
        id='datatable',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
        ],
        data=data.to_dict(),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="multi",
        row_selectable="multi",
        row_deletable=False,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=20,
    )
])

def get_index_and_column(previous, current):
    idx_changed = -1
    column_changed = None
    for i in range(len(current)):
        for column in current[i].keys():
            if previous[i][column] != current[i][column]:
                idx_changed = i
                column_changed = column
                break
        if idx_changed != -1 and column_changed is not None:
            break
    return idx_changed, column_changed

@app.callback(
    Output('datatable-update-container', 'children'),
    [Input('datatable', 'data_previous')],
    [State('datatable', 'data')])
def check_data_change(previous, current):
    if previous is None:
        dash.exceptions.PreventUpdate()
    else:
        idx_changed, column_changed = get_index_and_column(previous, current)
        data.update(idx_changed, column_changed, current[idx_changed][column_changed])
        return [f'Value Updated!']

if __name__ == "__main__":
    app.run_server(debug=True)
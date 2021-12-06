import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from data_model import ColumnBasedModel
from datetime import datetime

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
    html.Button('Return to Original Schema', id='return-to-original', n_clicks=0),
    html.Button('Revert Last Action', id='revert-action', n_clicks=0),
    html.Button('Revert All Actions', id='revert-all-action', n_clicks=0),
    html.Button('Save Changes to Database', id='save-to-database', n_clicks=0),
    html.Div(id='save-to-database-container'),
    dash_table.DataTable(
        id='datatable',
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns
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

def convert_column(column_names: list):
    columns = []
    for column in column_names:
        columns.append(
            {'name': column, 'id': column, 'deletable': False, 'selectable': True}
        )
    return columns

@app.callback(
    [Output('datatable', 'data'),
     Output('datatable-interactivity-container', 'children'),
     Output('datatable', 'selected_rows'),
     Output('datatable', 'selected_columns'),
     Output('datatable', 'columns')],
    [Input('delete', 'n_clicks'),
     Input('display-selected-column', 'n_clicks'),
     Input('return-to-original', 'n_clicks'),
     Input('revert-action', 'n_clicks'),
     Input('revert-all-action', 'n_clicks'),
     Input('save-to-database', 'n_clicks'),
     Input('datatable', 'selected_rows'),
     Input('datatable', 'selected_columns')],
    [State('datatable', 'data_previous'),
     State('datatable', 'data'),
     State('datatable', 'columns')])
def change_datatable_state(delete, display_selected_column, return_to_original, revert_last_action,
                           revert_all_action, save_to_database, row_indices, columns, previous, current, schema):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'delete' in changed_id:
        if data.delete(row_indices):
            return data.to_dict(), [f'Just Deleted Selected Tuples!'], [], columns, schema
        else:
            return current, [f'No Tuple is Selected!'], [], columns, schema
    elif 'display-selected-column' in changed_id:
        if data.change_display_columns(columns):
            return data.to_dict(), [f'Displaying Selected Columns!'], row_indices, columns, \
                   convert_column(data.to_schema())
        else:
            return current, [f'No Column is Selected!'], row_indices, columns, schema
    elif 'return-to-original' in changed_id:
        original_schema = list(df.columns)
        if data.change_display_columns(original_schema):
            return data.to_dict(), [f'Datatable has Returned to Original!'], row_indices, [], \
                   convert_column(original_schema)
    elif 'revert-action' in changed_id:
        action_type = data.revert()
        if action_type is not None:
            return data.to_dict(), [f'Last {action_type} has been Reverted!'], row_indices, columns, schema
        else:
            return current, ['No Action To Revert!'], row_indices, columns, schema
    elif 'revert-all-action' in changed_id:
        if data.last_actions:
            if data.reload(df.to_dict('records')):
                return data.to_dict(), [f'All Actions has been Reverted!'], row_indices, columns, schema
            else:
                return current, [f'Actions Cannot be Reverted! Data schema has changed!'], row_indices, columns, \
                       schema
        else:
            return current, [f'No Action has been taken so far!'], row_indices, columns, schema
    elif 'save-to-database' in changed_id:
        if data.save_progress():
            current_data = pd.DataFrame(data.to_dict())
            now = datetime.now()
            dt_string = now.strftime("%H%M%S_%d%m%Y")
            path = f"./datatable_{dt_string}.csv"
            current_data.to_csv(path)
            return current, [f'All changes has been saved!'], row_indices, columns, schema
        else:
            return current, [f'Oops! Something went wrong when trying to save progress!'], row_indices, columns, schema
    return current, [''], row_indices, columns, schema

if __name__ == "__main__":
    app.run_server(debug=True)
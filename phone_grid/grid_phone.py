# $ python3 -m venv venv
# $ source venv/bin/activate
# $ python -m pip install dash==1.13.3 pandas==1.0.5
# python3 grid_phone.py
# http://localhost:8050
import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

deleted_records = []
old_records = []
new_records = []
last_action = []

df = pd.read_csv("20191226-items.csv")
df = df.query("brand == 'Motorola' or brand == 'Nokia'or brand == 'Samsung' or brand == 'Sony' or brand == 'Apple' or brand == 'Xiaomi' or brand == 'HUAWEI' or brand == 'OnePlus' or brand == 'Google' or brand == 'ASUS'")
df.sort_values("title", inplace=True)

app = dash.Dash(__name__)


app.layout = html.Div([
    html.Div(id='datatable-interactivity-container'),
    html.Div(id='datatable-update-container'),
    html.Button('Revert Last Action', id='revert-action', n_clicks=0),
    html.Button('Revert All Actions', id='revert-all-action', n_clicks=0),
    html.Button('Save Changes to Database', id='save-to-database', n_clicks=0),
    html.Div(id='save-to-database-container'),
    dash_table.DataTable(
        id='datatable',
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
        page_current=0,
        page_size=50,
    )
])


@app.callback(
    Output('datatable-update-container', 'children'),
    [Input('datatable', 'data_previous')],
    [State('datatable', 'data')])
def check_data_change(previous, current):
    if previous is None:
        dash.exceptions.PreventUpdate()
    else:
        deleted_data = [row for row in previous if row not in current]
        if not deleted_data:
            return ['']
        for record in current:
            current_asin = record['asin']
            if current_asin == deleted_data[0]['asin']:
                assert len(new_records) == len(old_records)
                new_records.append(record)
                old_records.append(deleted_data[0])
                last_action.append('Modification')
                return [f'Just updated {current_asin}!']
        deleted_asin = deleted_data[0]['asin']
        deleted_title = deleted_data[0]['title']
        deleted_records.append(deleted_data[0])
        last_action.append('Deletion')
        return [f'Just removed {deleted_asin}: {deleted_title}!']


@app.callback(
    [Output('datatable', 'data'),
     Output('datatable-interactivity-container', 'children')],
    [Input('revert-action', 'n_clicks'),
     Input('revert-all-action', 'n_clicks')],
    [State('datatable', 'data_previous'),
     State('datatable', 'data')])
def revert_action(last_action_n_clicks, all_n_clicks, previous, current):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'revert-action' in changed_id:
        if last_action:
            return revert_one_action(current), ['Just Revert Last Action!']
    if 'revert-all-action' in changed_id:
        if last_action:
            while last_action or new_records or old_records or deleted_records:
                last_action.pop(0)
                if new_records:
                    new_records.pop(0)
                    old_records.pop(0)
                if deleted_records:
                    deleted_records.pop(0)
            return df.to_dict('records'), ['Just Restore Database to Original!']
    return current, ['']


def revert_one_action(current):
    reverted_state = current.copy()

    final_action = last_action.pop(-1)
    if final_action == 'Deletion':
        deleted_record = deleted_records.pop(-1)
        reverted_state.insert(0, deleted_record)
    elif final_action == 'Modification':
        inserted_record = new_records.pop(-1)
        deleted_record = old_records.pop(-1)
        index = reverted_state.index(inserted_record)
        reverted_state.insert(index, deleted_record)
        reverted_state.remove(inserted_record)
    return reverted_state


@app.callback(
    Output('save-to-database-container', 'children'),
    [Input('save-to-database', 'n_clicks')]
)
def save_to_database(n_clicks):
    if n_clicks > 0:
        if make_change_to_dataframe(df):
            return ['Progress Saved to Database!']
        else:
            return ['No Actions to Save to Database!']


def make_change_to_dataframe(dataframe):
    final = None
    assert len(last_action) == len(new_records) + len(deleted_records)
    for i in range(len(last_action)):
        final = 1
        action = last_action.pop(0)
        if action == 'Deletion':
            deleted_record = deleted_records.pop(0)
            deleted_asin = deleted_record['asin']
            index_names = dataframe[dataframe['asin'] == deleted_asin].index
            dataframe.drop(index_names, inplace=True)
        elif action == 'Modification':
            inserted_record = new_records.pop(0)
            inserted_asin = inserted_record['asin']
            deleted_record = old_records.pop(0)
            deleted_asin = deleted_record['asin']
            assert inserted_asin == deleted_asin
            index_names = dataframe[dataframe['asin'] == deleted_asin].index
            dataframe.drop(index_names, inplace=True)
            dataframe = dataframe.append(inserted_record, ignore_index=True)
    if final is not None:
        dataframe.to_csv('./new_database.csv')
        return True
    else:
        return False


if __name__ == "__main__":
    app.run_server(debug=True)
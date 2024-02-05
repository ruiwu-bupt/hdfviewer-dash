from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import feffery_antd_components as fac

import base64
import datetime
import io

import pandas as pd

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div([dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div(id='output-tree'),
            ], width=6
            ),
            dbc.Col([
                html.Div(id='output-tables'),
            ], width=6
            )
        ]
        ),
    ])])
    
])

def parse_contents(contents, filename: str, date) -> dict[str, pd.DataFrame]:
    _, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    if not filename.endswith('.h5') and not filename.endswith('.hdf5'):
        return html.Div([
            'invalid file, must be h5 or hdf5'
        ])
    with open(filename, 'wb') as f:
        f.write(decoded)
    hdf = pd.HDFStore(filename)
    keys = hdf.keys()
    return keys, parse_ant_tree(keys), {key: hdf[key].to_dict('records') for key in keys}

def parse_ant_tree(keys: list[str]):
    keys.sort()
    keys = [key.split('/') for key in keys]
    tree_data = []
    for key in keys:
        cur = tree_data
        for key_part in key:
            if not key_part:
                continue
            found = False
            for cur_key_part in cur:
                if cur_key_part['key'] == key_part:
                    cur = cur_key_part['children']
                    found = True
                    break
            if not found:
                cur.append({'key': key_part, 'title': key_part, 'children': []})
                cur = cur[-1]['children']
    print(tree_data)
    return tree_data

@callback(
    [
        Output('output-tree', 'children'),
        Output('output-tables', 'children'),
    ],
    [
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        State('upload-data', 'last_modified')
    ]
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        keys, tree, tables = parse_contents(list_of_contents[0], list_of_names[0], list_of_dates[0])
        return fac.AntdTree(treeData=tree, defaultExpandAll=True), dcc.Tabs(
            id="tab",
            value=keys[0],
            children=[
                dcc.Tab(
                    label=key.split('/')[-1],
                    value=key,
                    children=[
                        dash_table.DataTable(data=tables[key], page_size=100, sort_action='native')
                    ],
                )
                for key in tables
            ],
        )
    return html.Div(), html.Div()


if __name__ == '__main__':
    app.run(debug=True)

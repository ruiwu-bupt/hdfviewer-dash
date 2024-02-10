import json
import base64

from dash import Dash, dcc, html, dash_table, Input, Output
from dash import State, callback, ctx
from dash.exceptions import PreventUpdate
import plotly.express as px
import dash_bootstrap_components as dbc
import feffery_antd_components as fac

import pandas as pd

app = Dash(__name__, title="hdfplotter",
           external_stylesheets=[dbc.themes.BOOTSTRAP])

tables_navigation = [
    html.Div(id='output-tree'),
    html.Div(id='output-attrs')
]

tables_tab = dbc.Tab(
    label='tables',
    tab_id='tables',
    children=[
        dbc.Container([
            # dcc.Loading(
                dbc.Row([
                    dbc.Col(tables_navigation,
                        width=4,
                            ),
                    dbc.Col([
                        html.Div(id='output-tables'),

                    ], width=8
                    )
                ]
                )
            # ),

        ]),
    ],
    label_style={"color": "black"},
    active_label_style={"color": "blue"},
)


def input_box(info, component):
    return html.Div([
        dbc.Label(f'{info}'),
        html.Div([component])
    ])


plot_configs = dbc.Col([
    input_box(
        "数据集",
        dcc.Dropdown(id='dataset'),
    ),
    input_box(
        "绘图类型",
        dcc.Dropdown(id='figure-type',
                     placeholder="绘图类型",
                     options=[
                         {"label": "折线图", "value": "line"},
                         {"label": "散点图", "value": "scatter"},
                     ],
                     value='line'),
    ),
    input_box("X轴", dcc.Dropdown(id='x-axis')),
    input_box("Y轴", dcc.Dropdown(id='y-axis')),
    input_box("分组", dcc.Dropdown(id='groupby')),
    input_box("标题", dbc.Input(id='title', type="text")),
    input_box("X轴名称", dbc.Input(id='x-label', type="text")),
    input_box("Y轴名称", dbc.Input(id='y-label', type="text")),
], width=3)

plot_fig = dbc.Col([
    dcc.Graph(id='plot-fig'),
], width=9)

plot_frame = html.Div([dbc.Container([
    dbc.Row([plot_configs,
             plot_fig])])

])

plot_tab = dbc.Tab(
    label='plots',
    tab_id='plots',
    children=[
        plot_frame
    ],
    label_style={"color": "black"},
    active_label_style={"color": "blue"},
)

main_tabs = dbc.Tabs(
    id="main-tabs",
    key="main-tabs",
    children=[
        tables_tab,
        plot_tab,
    ],
)

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
    dcc.Store(id="attrs"),
    dcc.Store(id="df_records"),
    html.Div([main_tabs])

])


def parse_contents(contents, filename: str, date):
    _, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    if not filename.endswith('.h5') and not filename.endswith('.hdf5'):
        return html.Div([
            'invalid file, must be h5 or hdf5'
        ])
    with open(filename, 'wb') as f:
        f.write(decoded)
    hdf = pd.HDFStore(filename)
    keys, tree_data = parse_ant_tree(hdf.keys())
    attrs = {}
    for key in keys:
        attrs[key] = repr(hdf.get_storer(key).attrs)
    return keys, attrs, tree_data, {key: hdf[key].to_dict('records') for key in keys}


def parse_ant_tree(keys: list[str]):
    keys.sort()
    keys = [key.split('/') for key in keys]
    processed_keys = []
    tree_data = []
    for key in keys:
        cur_pos = tree_data
        titles = []
        for title in key:
            if not title:
                continue
            titles.append(title)
            cur_key = "/".join(titles)
            found = False
            for match_cur_key in cur_pos:
                if match_cur_key['key'] == cur_key:
                    cur_pos = match_cur_key['children']
                    found = True
                    break
            if not found:
                cur_pos.append(
                    {'key': cur_key, 'title': title, 'children': []})
                cur_pos = cur_pos[-1]['children']
        processed_keys.append('/'.join(titles))
    return processed_keys, tree_data


@callback(
    [
        Output('attrs', 'data'),
        Output('df_records', 'data'),
        Output('output-tree', 'children'),
        Output('output-tables', 'children'),
        Output('dataset', 'options'),
    ],
    [
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        State('upload-data', 'last_modified')
    ],
    prevent_initial_call=True
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        keys, attrs, tree, tables = parse_contents(
            list_of_contents[0], list_of_names[0], list_of_dates[0])
        return attrs, tables, \
            fac.AntdTree(id={"type": "tree", "index": 0},
                         treeData=tree, defaultExpandAll=True), \
            dbc.Tabs(
                id={"type": "tabs", "index": 0},
                key=keys[0],
                children=[
                    dbc.Tab(
                        label=key.split('/')[-1],
                        tab_id=key,
                        children=[
                            dash_table.DataTable(
                                data=tables[key], page_size=100, sort_action='native')
                        ],
                        label_style={"color": "black"},
                        active_label_style={"color": "blue"},
                    )
                    for key in keys
                ],
            ), \
            list(attrs.keys())
    return {}, {}, html.Div(), html.Div(), []


@callback(
    Output({"type": "tree", "index": 0}, "selectedKeys"),
    Output("output-attrs", "children"),
    Output({"type": "tabs", "index": 0}, "active_tab"),
    Input({"type": "tree", "index": 0}, "selectedKeys"),
    Input({"type": "tabs", "index": 0}, "active_tab"),
    State("attrs", "data"),
    prevent_initial_call=True
)
def update_current_tab(tree_selected_keys, tabs_current_tab, attrs):
    trigger_info = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger_info == "attrs":
        raise PreventUpdate
    trigger_type = json.loads(trigger_info)['type']
    value = tree_selected_keys[0] if trigger_type == "tree" else tabs_current_tab
    if value not in attrs:
        raise PreventUpdate
    # 服了，弱智错误看了两个小时，id写重了，就会有各种莫名其妙的问题
    return [value], dbc.Textarea(id="attrs-textarea", value=attrs[value], readonly=True, rows=10), value

@callback(
    Output({"type": "tree", "index": 0}, "scrollTarget"),
    Input({"type": "tabs", "index": 0}, "active_tab"),
    prevent_initial_call=True
)
def scroll_target_node(tabs_current_tab):
    # TODO: 这里还需要配置自动展开
    scroll_dict = {"key": tabs_current_tab, "align": "auto"}
    return scroll_dict

@callback(
    Output("x-axis", "options"),
    Output("y-axis", "options"),
    Output("groupby", "options"),
    Input("dataset", "value"),
    State("df_records", "data"),
    prevent_initial_call=True
)
def update_plot_configs(value, data):
    if not data or not data[value]:
        raise PreventUpdate
    columns = list(data[value][0].keys())
    return columns, columns, columns


@callback(
    Output("plot-fig", "figure"),
    Input("dataset", "value"),
    Input("figure-type", "value"),
    Input("title", "value"),
    Input("x-axis", "value"),
    Input("y-axis", "value"),
    Input("x-label", "value"),
    Input("y-label", "value"),
    Input("groupby", "value"),
    State("df_records", "data"),
    prevent_initial_call=True
)
def update_plot_figure(dataset, figure_type, title, x_axis, y_axis,
                       x_label, y_label, grouby, df_records):
    if not (x_axis and y_axis):
        raise PreventUpdate
    df = pd.DataFrame.from_records(df_records[dataset])
    if not (x_axis in df and y_axis in df):
        raise PreventUpdate
    labels = {}
    if x_label:
        labels[x_axis] = x_label
    if y_label:
        labels[y_axis] = y_label
    
    color = None
    if grouby:
        color = grouby
    plot_kwargs = {
        "x": x_axis,
        "y": y_axis,
        "title": title,
        "labels": labels,
        "color": color,
    }
    match figure_type:
        case "line":
            return px.line(df, **plot_kwargs)
        case "scatter":
            return px.scatter(df, **plot_kwargs)


if __name__ == '__main__':
    app.run(debug=True)

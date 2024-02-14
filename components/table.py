import base64

import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dash_table, Input, Output
from dash import State, callback, no_update
from dash.exceptions import PreventUpdate
import feffery_antd_components as fac

from components.plot import dataset_all


class H5FileTypeException(Exception):
    pass


h5_warning_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("不支持的文件格式")),
        dbc.ModalBody("请上传HDF5文件(*.hdf5或*.h5)"),
    ],
    id="h5_warning_modal",
    centered=True,
    is_open=False,
)

tables_navigation = [
    html.Div(id='output-tree'),
    html.Div(id='output-attrs')
]

tables_tab = dbc.Tab(
    label='数据表',
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


def parse_contents(contents, filename: str, date):
    _, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    if not filename.endswith('.h5') and not filename.endswith('.hdf5'):
        raise H5FileTypeException
    with open(filename, 'wb') as f:
        f.write(decoded)
    hdf = pd.HDFStore(filename)
    keys, tree_data = parse_ant_tree(hdf.keys())
    attrs = {}
    for key in keys:
        attrs[key] = repr(hdf.get_storer(key).attrs)
    return attrs, tree_data, {key: hdf[key].to_dict('records') for key in keys}


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

# @callback(
#     Output({"type": "tree", "index": 0}, "selectedKeys"),
#     Output("output-attrs", "children"),
#     Output({"type": "tabs", "index": 0}, "active_tab"),
#     Input({"type": "tree", "index": 0}, "selectedKeys"),
#     Input({"type": "tabs", "index": 0}, "active_tab"),
#     State("attrs", "data"),
#     prevent_initial_call=True
# )
# def update_current_tab(tree_selected_keys, tabs_current_tab, attrs):
#     trigger_info = ctx.triggered[0]["prop_id"].split(".")[0]
#     if trigger_info == "attrs":
#         raise PreventUpdate
#     trigger_type = json.loads(trigger_info)['type']
#     value = tree_selected_keys[0] if trigger_type == "tree" else tabs_current_tab
#     if value not in attrs:
#         raise PreventUpdate
#     # 服了，弱智错误看了两个小时，id写重了，就会有各种莫名其妙的问题
#     return [value], dbc.Textarea(id="attrs-textarea", value=attrs[value], readonly=True, rows=10), value


# @callback(
#     Output({"type": "tree", "index": 0}, "scrollTarget"),
#     Input({"type": "tabs", "index": 0}, "active_tab"),
#     prevent_initial_call=True
# )
# def scroll_target_node(tabs_current_tab):
#     # TODO: 这里还需要配置自动展开
#     scroll_dict = {"key": tabs_current_tab, "align": "auto"}
#     return scroll_dict

@callback(
    [
        Output('h5_warning_modal', 'is_open'),
        Output('attrs', 'data'),
        Output('df_records', 'data'),
        Output('output-tree', 'children'),
        Output('output-tables', 'children'),
        Output(dataset_all, 'options'),
    ],
    [
        State('input-pages', 'children'),
        Input('upload_data', 'contents'),
        State('upload_data', 'filename'),
        State('upload_data', 'last_modified')
    ],
    prevent_initial_call=True
)
def update_output(input_pages, file_content, file_name, file_ts):
    if file_content is not None:
        try:
            attrs, tree, tables = parse_contents(
                file_content, file_name, file_ts)
        except H5FileTypeException:
            return True, no_update, no_update, no_update, no_update, [no_update]*len(input_pages)
        keys = list(attrs.keys())
        return False, attrs, tables, \
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
            [keys for _ in range(len(input_pages))]
    raise PreventUpdate

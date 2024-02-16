import uuid

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
from dash import State, callback, Patch
from dash.exceptions import PreventUpdate

from utils.common import *

filter_operators = [
    {'label': '>', 'value': '>'},
    {'label': '<', 'value': '<'},
    {'label': '>=', 'value': '>='},
    {'label': '<=', 'value': '<='},
    {'label': '=', 'value': '=='},
    {'label': '!=', 'value': '!='},
]


def gen_filter_box(cols, ops):
    cid = str(uuid.uuid1())
    return html.Span([
        dcc.Dropdown(
            options=cols,
            placeholder='列名',
            clearable=False,
        ),
        dcc.Dropdown(
            options=ops,
            placeholder='操作符',
            clearable=False,
        ),
        dcc.Input(type='text'),
        dbc.Button('Delete', color='light', className='me-1',
                   id=gen_id(filter_delete, cid),),
    ],
        # BUG: 人麻了，{'type:': 'filter_box', 'index': cid}
        # 硬编码果然要人命
        id=gen_id(filter_box, cid),
        style={'display': 'flex'}
    )


def gen_filter_boxes(cid, cols):
    return html.Span([
        gen_filter_box(cols, filter_operators),
    ],
        id=gen_id(filter_boxes, cid)
    )


@callback(
    Output(filter_boxes_match, 'children', allow_duplicate=True),
    Input(filter_add_match, 'n_clicks'),
    State('df_records', 'data'),
    State(dataset_match, 'value'),
    State(filter_boxes_match, 'children'),
    prevent_initial_call=True
)
def add_filter(n_clicks, data, dataset, children):
    if not n_clicks or not data or not dataset:
        raise PreventUpdate
    keys = list(data[dataset][0].keys())
    children.append(gen_filter_box(keys, filter_operators))
    return children


@callback(
    Output(filter_box_match, 'style'),
    Input(filter_delete_match, 'n_clicks'),
    prevent_initial_call=True,
)
def delete_filter(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return {'display': 'None'}


def gen_filter_modal(cid, cols):
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle('筛选列')),
            dbc.ModalBody([
                gen_filter_boxes(cid, cols),
                dbc.Button('Add', color='light', className='me-1',
                           id=gen_id(filter_add, cid)),
            ],),
            dbc.ModalFooter(
                dbc.Button(
                    '确认',
                    id=gen_id(filter_modal_ok, cid),
                    className='ms-auto',
                    n_clicks=0,
                )
            ),
        ],
        id=gen_id(filter_modal, cid),
        centered=True,
        scrollable=True,
        is_open=False,
        size='l',
        backdrop=False
    )


@callback(
    Output(filter_modal_match, 'is_open'),
    Input(show_filter_button_match, 'n_clicks'),
    prevent_initial_call=True,
)
def show_filter_modal(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return True


@callback(
    Output(plot_configs_match, 'data'),
    Output(filter_cnt_match, 'children'),
    Input(filter_modal_ok_match, 'n_clicks'),
    State(filter_boxes_match, 'children'),
    prevent_initial_call=True,
)
def update_filter_configs(n_clicks, children):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    filter_configs_match_patch = Patch()
    configs = []
    for child in children:
        filter_box_hidden = child['props'].get(
            'style', {}).get('display', None) == 'None'
        if filter_box_hidden:
            continue
        filter_box = child['props']['children']
        filter_col_name = filter_box[0]['props'].get('value', None)
        filter_col_op = filter_box[1]['props'].get('value', None)
        filter_col_val = filter_box[2]['props'].get('value', None)
        config = [filter_col_name, filter_col_op, filter_col_val]
        if not all(config):
            continue
        configs.append(config)
    filter_configs_match_patch['filter'] = configs
    return filter_configs_match_patch, f'当前共{len(configs)}个筛选条件'


@callback(
    Output(filter_modal_match, 'is_open', allow_duplicate=True),
    Input(filter_modal_ok_match, 'n_clicks'),
    prevent_initial_call=True,
)
def close_modal(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return False

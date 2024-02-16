import uuid
import operator

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
from dash import State, callback, Patch
from dash.exceptions import PreventUpdate

from utils.common import *

compute_operators = [
    {'label': '+', 'value': '+'},
    {'label': '-', 'value': '-'},
    {'label': '*', 'value': '*'},
    {'label': '/', 'value': '/'},
]

compute_func = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
}


def gen_compute_box(cols, ops):
    cid = str(uuid.uuid1())
    return html.Span([
        dbc.Label('G0:'),
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
        dcc.Dropdown(
            options=cols,
            placeholder='列名',
            clearable=False,
        ),
        dbc.Button('Delete', color='light', className='me-1',
                   id=gen_id(compute_delete, cid),),
    ],
        id=gen_id(compute_box, cid),
        style={'display': 'flex'}
    )


def gen_compute_boxes(cid, cols):
    return html.Span([
        gen_compute_box(cols, compute_operators),
    ],
        id=gen_id(compute_boxes, cid)
    )


@callback(
    Output(compute_boxes_match, 'children', allow_duplicate=True),
    Input(compute_add_match, 'n_clicks'),
    State('df_records', 'data'),
    State(dataset_match, 'value'),
    State(compute_boxes_match, 'children'),
    prevent_initial_call=True
)
def add_compute(n_clicks, data, dataset, children):
    if not n_clicks or not data or not dataset:
        raise PreventUpdate
    keys = list(data[dataset][0].keys())
    children.append(gen_compute_box(keys, compute_operators))
    return children


@callback(
    Output(compute_box_match, 'style'),
    Input(compute_delete_match, 'n_clicks'),
    prevent_initial_call=True,
)
def delete_compute(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return {'display': 'None'}


def gen_compute_modal(cid, cols):
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle('计算列')),
            dbc.ModalBody([
                gen_compute_boxes(cid, cols),
                dbc.Button('Add', color='light', className='me-1',
                           id=gen_id(compute_add, cid)),
            ],),
            dbc.ModalFooter(
                dbc.Button(
                    '确认',
                    id=gen_id(compute_modal_ok, cid),
                    className='ms-auto',
                    n_clicks=0,
                )
            ),
        ],
        id=gen_id(compute_modal, cid),
        centered=True,
        scrollable=True,
        is_open=False,
        size='l',
        backdrop=False
    )


@callback(
    Output(compute_modal_match, 'is_open'),
    Input(show_compute_button_match, 'n_clicks'),
    prevent_initial_call=True,
)
def show_compute_modal(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return True


@callback(
    Output(compute_store_match, 'data', allow_duplicate=True),
    Output(compute_cnt_match, 'children'),
    Input(compute_modal_ok_match, 'n_clicks'),
    State(compute_boxes_match, 'children'),
    prevent_initial_call=True,
)
def update_compute_configs(n_clicks, children):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    compute_configs = {}
    configs = []
    for child in children:
        compute_box_hidden = child['props'].get(
            'style', {}).get('display', None) == 'None'
        if compute_box_hidden:
            continue
        compute_box = child['props']['children']
        # TODO: GO: fix here
        compute_col_name = compute_box[0]['props'].get('children', None)
        compute_col_name1 = compute_box[1]['props'].get('value', None)
        compute_col_op = compute_box[2]['props'].get('value', None)
        compute_col_name2 = compute_box[3]['props'].get('value', None)
        config = [compute_col_name, compute_col_name1, compute_col_op, compute_col_name2]
        if not all(config):
            continue
        configs.append(config)
    compute_configs['compute'] = configs
    return compute_configs, f'当前共{len(configs)}个计算列'


@callback(
    Output(compute_modal_match, 'is_open', allow_duplicate=True),
    Input(compute_modal_ok_match, 'n_clicks'),
    prevent_initial_call=True,
)
def close_modal(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return False

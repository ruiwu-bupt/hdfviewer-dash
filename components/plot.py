import uuid
from operator import methodcaller

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
from dash import State, callback, ctx, Patch
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import pandas as pd

from components.filter import filter_boxes_match, gen_filter_modal
from components.compute import gen_compute_modal, compute_func
from utils.common import *


def input_box(info, component):
    return html.Div([
        dbc.Label(info),
        html.Div([component])
    ])


def input_page(title, cols=[]):
    cid = str(uuid.uuid1())
    return dbc.Card(
        [
            dcc.Store(id={'type': 'plot-configs', 'index': cid}, data={}),
            dcc.Store(id=gen_id(compute_store, cid), data={}),
            html.Span([
                dbc.Label(title),
                dbc.Button('Delete', color='light', className='me-1',
                           id={'type': 'page-delete', 'index': cid}),
            ]),
            input_box(
                '数据集',
                dcc.Dropdown(
                    id={'type': 'dataset', 'index': cid},
                    options=cols,
                    clearable=False),
            ),
            input_box(
                '绘图类型',
                dcc.Dropdown(id={'type': 'figure-type', 'index': cid},
                             placeholder='绘图类型',
                             clearable=False,
                             options=[
                                 {'label': '折线图', 'value': 'lines'},
                                 {'label': '散点图', 'value': 'markers'},
                ],
                    value='lines'),
            ),
            input_box('X轴', dcc.Dropdown(
                id={'type': 'x-axis', 'index': cid}, options=cols, clearable=False)),
            input_box('Y轴', dcc.Dropdown(
                id={'type': 'y-axis', 'index': cid}, options=cols, clearable=False)),
            input_box('分组', dcc.Dropdown(
                id={'type': 'groupby', 'index': cid}, options=cols)),
            input_box('聚合类型', dcc.Dropdown(
                id={'type': 'agg_type', 'index': cid}, options=[
                    {'label': '最大值', 'value': 'max'},
                    {'label': '最小值', 'value': 'min'},
                    {'label': '平均数', 'value': 'mean'},
                    {'label': '中位数', 'value': 'median'},
                    {'label': '计数', 'value': 'count'},
                    {'label': '标准差', 'value': 'std'},
                    {'label': '和值', 'value': 'sum'},
                    # {'label': '最大值-最小值', 'value': 'max-min'},
                ])),
            input_box('聚合列', dcc.Dropdown(
                id={'type': 'agg_col', 'index': cid}, options=cols)),
            html.Span([
                # BUG: 睿智问题，id的type没写对
                dbc.Button('增加筛选条件', color='light', className='me-1',
                           id={'type': 'show-filter-button', 'index': cid}),
                dbc.Label('当前共0个筛选条件', id={
                          'type': 'filter-cnt', 'index': cid}),
            ]),
            gen_filter_modal(cid, cols),
            html.Span([
                dbc.Button('增加计算列', color='light', className='me-1',
                           id={'type': 'show-compute-button', 'index': cid}),
                dbc.Label('当前共0个计算列', id={
                          'type': 'compute-cnt', 'index': cid}),
            ],),
            gen_compute_modal(cid, cols),

        ],
        id={'type': 'input-page', 'index': cid},
        body=True,
        style={'background-color': '#f3f6fa'}
    )


plot_configs = dbc.Col([
    html.Div([
        input_page('图表页'),
    ], id='input-pages'),
    dbc.Button('Add', color='light', className='me-1', id='page-add'),
    input_box('标题', dbc.Input(id='title', type='text')),
    input_box('X轴名称', dbc.Input(id='x-label', type='text')),
    input_box('Y轴名称', dbc.Input(id='y-label', type='text'))
], width=3, style={'overflow': 'scroll'})

plot_fig = dbc.Col([
    dcc.Store(id='plot-attrs'),
    dcc.Graph(id='plot-fig', figure=go.Figure(),
              config={'displaylogo': False}),
], width=9)

plot_frame = html.Div([dbc.Container([
    dbc.Row([
        plot_fig,
        plot_configs,
    ])])

])

plot_tab = dbc.Tab(
    label='绘图',
    tab_id='plots',
    children=[
        plot_frame
    ],
    label_style={'color': 'black'},
    active_label_style={'color': 'blue'},
)


@callback(
    Output(filter_boxes_match, 'children'),
    Output(compute_boxes_match, 'children'),
    Output(x_axis_match, 'options'),
    Output(y_axis_match, 'options'),
    Output(groupby_match, 'options'),
    Output(agg_col_match, 'options'),
    Input(dataset_match, 'value'),
    State('df_records', 'data'),
    Input(compute_store_match, 'data'),
    State(filter_boxes_match, 'children'),
    State(compute_boxes_match, 'children'),
    prevent_initial_call=True
)
def update_available_cols(dataset, df, compute_configs, filter_col_boxes, compute_cols_boxes):
    if not df or not df[dataset]:
        raise PreventUpdate
    patch_filter = Patch()
    patch_compute = Patch()
    origin_cols = list(df[dataset][0].keys())
    compute_cols = [item[0] for item in compute_configs.get('compute', [])]
    # TODO: 切换dataset会导致某些计算列丢失，需要好好想想切换dataset的时候dropdown控件的行为
    columns = origin_cols + compute_cols
    for i in range(len(filter_col_boxes)):
        # TODO: 這裡硬編碼太惡心了
        # TODO: 状态更新在不同的output模块，需要拆开写callback吗？
        patch_filter[i]['props']['children'][0]['props']['options'] = columns
    for i in range(len(filter_col_boxes)):
        patch_compute[i]['props']['children'][1]['props']['options'] = origin_cols
        patch_compute[i]['props']['children'][3]['props']['options'] = origin_cols
    return patch_filter, patch_compute, columns, columns, columns, columns


@callback(
    Output(plot_configs_match, 'data', allow_duplicate=True),
    Input(dataset_match, 'value'),
    Input(figure_type_match, 'value'),
    Input(x_axis_match, 'value'),
    Input(y_axis_match, 'value'),
    Input(groupby_match, 'value'),
    Input(agg_type_match, 'value'),
    Input(agg_col_match, 'value'),
    Input(compute_store_match, 'data'),
    prevent_initial_call=True
)
def update_plot_configs(dataset, figure_type, x_axis, y_axis, grouby, agg_type, agg_col, compute_configs):
    patch = Patch()
    patch['basic'] = {
        'dataset': dataset,
        'figure_type': figure_type,
        'x_axis': x_axis,
        'y_axis': y_axis,
        'groupby': grouby,
        'agg_type': agg_type,
        'agg_col': agg_col,
    }
    patch['compute'] = compute_configs.get('compute', [])
    return patch


@callback(
    Output('input-pages', 'children'),
    Input('page-add', 'n_clicks'),
    State('input-pages', 'children'),
    State('attrs', 'data'),
    prevent_initial_call=True
)
def add_input_page(n_clicks, input_pages, attrs):
    cnt = 0
    # for child in input_pages:
    #     style = child['props']['style']
    #     if style.get('display', '') != 'None':
    #         cnt += 1
    cnt = len(input_pages)
    page_patch = Patch()
    suffix = '' if cnt == 0 else str(cnt)
    opts = list(attrs.keys())
    page_patch.append(input_page(f'图表页{suffix}', opts))
    return page_patch


@callback(
    Output(input_page_match, 'style'),
    Output(plot_configs_match, 'data', allow_duplicate=True),
    Input(page_delete_match, 'n_clicks'),
    prevent_initial_call=True
)
def delete_input_page(n_clicks):
    # 草，dash写这种动态的回调太恶心了; 先用display none搞了
    # 对于新增加的input_page会触发删除按钮，而且prevent_initial_call不生效
    delete_page_patch = Patch()
    delete_page_patch['display'] = 'None'
    if n_clicks is None:
        raise PreventUpdate
    return delete_page_patch, delete_page_patch


@callback(
    Output('plot-fig', 'figure', allow_duplicate=True),

    Input(plot_configs_all, 'data'),

    State('title', 'value'),
    State('x-label', 'value'),
    State('y-label', 'value'),
    State('df_records', 'data'),
    prevent_initial_call=True
)
def update_multi_figures(plot_configs, title, x_label, y_label, df_records):
    if not df_records:
        raise PreventUpdate
    fig = go.Figure()
    fig.update_layout(title_text=title,
                      title_x=0.5,
                      xaxis_title_text=x_label,
                      yaxis_title_text=y_label)
    for plot_config in plot_configs:
        baisc_config = plot_config.get('basic', {})
        dataset = baisc_config.get('dataset', None)
        figure_type = baisc_config.get('figure_type', None)
        x_axis = baisc_config.get('x_axis', None)
        y_axis = baisc_config.get('y_axis', None)
        groupby = baisc_config.get('groupby', None)
        display = baisc_config.get('display', None)
        agg_type = baisc_config.get('agg_type', None)
        agg_col = baisc_config.get('agg_col', None)

        filters = plot_config.get('filter', [])
        computes = plot_config.get('compute', [])
        if display == 'None' or not dataset:
            continue
        # TODO: 这里的逻辑优化下
        # TODO: dataset 切换时，x_axis和y_axis可能还有值，但是已经不合法了，需要校验
        if not (x_axis and y_axis) and not (agg_type and groupby and agg_col):
            continue
        df = pd.DataFrame.from_records(df_records[dataset])
        if computes:
            for compute in computes:
                df[compute[0]] = compute_func[compute[2]](
                    df[compute[1]], df[compute[3]])
        if filters:
            query = ' & '.join(f'`{filter_col_name}` {filter_col_op} {filter_col_val}'
                               for filter_col_name, filter_col_op, filter_col_val in filters)
            df = df.query(query)
        if not groupby:
            name = f'{dataset}-{x_axis}-{y_axis}'
            fig.add_trace(
                go.Scatter(
                    x=df[x_axis],
                    y=df[y_axis],
                    name=name,
                    mode=figure_type,
                ))
        else:
            if not agg_type:
                # TODO: 只挑出带有x_axis和y_axis的列做groupby？
                groupby_pairs = df.groupby(groupby)
                for key, data in groupby_pairs:
                    name = f'{dataset}-{x_axis}-{y_axis}, {groupby}={key}'
                    fig.add_trace(
                        go.Scatter(
                            x=data[x_axis],
                            y=data[y_axis],
                            name=name,
                            mode=figure_type,
                        ))
            else:
                data = methodcaller(agg_type)(df.groupby(groupby))
                name = f'{dataset}-{groupby}(分组)-{agg_col}(聚合@{agg_type})'
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data[agg_col],
                        name=name,
                        mode=figure_type,
                    ))
    return fig


@callback(
    Output('plot-fig', 'figure', allow_duplicate=True),
    Input('title', 'value'),
    Input('x-label', 'value'),
    Input('y-label', 'value'),
    prevent_initial_call=True
)
def patch_plot_figure_label(title, x_label, y_label):
    trigger_info = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_info in ['title', 'x-label', 'y-label']:
        figure_patch = Patch()
        match trigger_info:
            case 'title':
                figure_patch.layout.title.text = title
                figure_patch.layout.title.x = 0.5
            case 'x-label':
                figure_patch.layout.xaxis.title.text = x_label
            case 'y-label':
                figure_patch.layout.yaxis.title.text = y_label
        return figure_patch

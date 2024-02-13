import uuid
from operator import methodcaller

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
from dash import State, callback, ctx, Patch, MATCH, ALL
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import pandas as pd


def input_box(info, component):
    return html.Div([
        dbc.Label(info),
        html.Div([component])
    ])


def input_page(title, opts=[]):
    cid = str(uuid.uuid1())
    return dbc.Card(
        [
            dcc.Store(id={"type": 'plot-configs', "index": cid}, data={}),
            html.Span([
                dbc.Label(title),
                dbc.Button("Delete", color="light", className="me-1",
                           id={"type": 'page-delete', "index": cid}),
            ]),
            input_box(
                "数据集",
                dcc.Dropdown(
                    id={"type": 'dataset', "index": cid},
                    options=opts,
                    clearable=False),
            ),
            input_box(
                "绘图类型",
                dcc.Dropdown(id={"type": 'figure-type', "index": cid},
                             placeholder="绘图类型",
                             clearable=False,
                             options=[
                                 {"label": "折线图", "value": "lines"},
                                 {"label": "散点图", "value": "markers"},
                ],
                    value='lines'),
            ),
            input_box("X轴", dcc.Dropdown(
                id={"type": 'x-axis', "index": cid}, options=opts, clearable=False)),
            input_box("Y轴", dcc.Dropdown(
                id={"type": 'y-axis', "index": cid}, options=opts, clearable=False)),
            input_box("分组", dcc.Dropdown(
                id={"type": 'groupby', "index": cid}, options=opts)),
            input_box("聚合类型", dcc.Dropdown(
                id={"type": 'agg_type', "index": cid}, options=[
                    {"label": "最大值", "value": "max"},
                    {"label": "最小值", "value": "min"},
                    {"label": "平均数", "value": "mean"},
                    {"label": "中位数", "value": "median"},
                    {"label": "计数", "value": "count"},
                    {"label": "标准差", "value": "std"},
                    {"label": "和值", "value": "sum"},
                    # {"label": "最大值-最小值", "value": "max-min"},
                ])),
            input_box("聚合列", dcc.Dropdown(
                id={"type": 'agg_col', "index": cid}, options=opts)),
            html.Span([
                dbc.Button("增加筛选条件", color="light", className="me-1",
                           id={"type": 'filter-modal', "index": cid}),
                dbc.Label("当前共0个筛选条件"),
            ]),
            html.Span([
                dbc.Button("增加计算列", color="light", className="me-1",
                           id={"type": 'compute-modal', "index": cid}),
                dbc.Label("当前共0个计算列"),
            ]),

        ],
        id={"type": "input-page", "index": cid},
        body=True,
        style={"background-color": "#f3f6fa"}
    )


plot_configs = dbc.Col([
    html.Div([
        input_page("图表页"),
    ], id="input-pages"),
    dbc.Button("Add", color="light", className="me-1", id="page-add"),
    input_box("标题", dbc.Input(id='title', type="text")),
    input_box("X轴名称", dbc.Input(id='x-label', type="text")),
    input_box("Y轴名称", dbc.Input(id='y-label', type="text"))
], width=3, style={"overflow": "scroll"})

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
    label_style={"color": "black"},
    active_label_style={"color": "blue"},
)


def o_match(tp):
    return {"type": tp, "index": MATCH}


def o_all(tp):
    return {"type": tp, "index": ALL}


x_axis_match = o_match('x-axis')
y_axis_match = o_match('y-axis')
dataset_match = o_match('dataset')
figure_type_match = o_match('figure-type')
groupby_match = o_match('groupby')
agg_type_match = o_match('agg_type')
agg_col_match = o_match('agg_col')
page_delete_match = o_match('page-delete')
input_page_match = o_match('input-page')
plot_configs_match = o_match('plot-configs')

x_axis_all = o_all('x-axis')
y_axis_all = o_all('y-axis')
dataset_all = o_all('dataset')
figure_type_all = o_all('figure-type')
groupby_all = o_all('groupby')
agg_type_all = o_all('agg_type')
agg_col_all = o_all('agg_col')
page_delete_all = o_all('page-delete')
plot_configs_all = o_all('plot-configs')


@callback(
    Output(x_axis_match, "options"),
    Output(y_axis_match, "options"),
    Output(groupby_match, "options"),
    Output(agg_col_match, "options"),
    Input(dataset_match, "value"),
    State("df_records", "data"),
    prevent_initial_call=True
)
def update_plot_configs(value, data):
    if not data or not data[value]:
        raise PreventUpdate
    columns = list(data[value][0].keys())
    return columns, columns, columns, columns


@callback(
    Output(plot_configs_match, "data"),
    Input(dataset_match, "value"),
    Input(figure_type_match, "value"),
    Input(x_axis_match, "value"),
    Input(y_axis_match, "value"),
    Input(groupby_match, "value"),
    Input(agg_type_match, "value"),
    Input(agg_col_match, "value"),
    prevent_initial_call=True
)
def update_plot_configs(dataset, figure_type, x_axis, y_axis, grouby, agg_type, agg_col):
    return {
        "dataset": dataset,
        "figure_type": figure_type,
        "x_axis": x_axis,
        "y_axis": y_axis,
        "groupby": grouby,
        "agg_type": agg_type,
        "agg_col": agg_col,
    }


@callback(
    Output("input-pages", "children"),
    Input("page-add", "n_clicks"),
    State("input-pages", "children"),
    State("attrs", "data"),
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
    suffix = "" if cnt == 0 else str(cnt)
    opts = list(attrs.keys())
    page_patch.append(input_page(f'图表页{suffix}', opts))
    return page_patch


@callback(
    Output(input_page_match, "style"),
    Output(plot_configs_match, "data", allow_duplicate=True),
    Input(page_delete_match, "n_clicks"),
    prevent_initial_call=True
)
def delete_input_page(n_clicks):
    # 草，dash写这种动态的回调太恶心了; 先用display none搞了
    # 对于新增加的input_page会触发删除按钮，而且prevent_initial_call不生效
    delete_page_patch = Patch()
    delete_page_patch['display'] = "None"
    if n_clicks is None:
        raise PreventUpdate
    return delete_page_patch, delete_page_patch


@callback(
    Output("plot-fig", "figure", allow_duplicate=True),

    Input(plot_configs_all, "data"),

    State("title", "value"),
    State("x-label", "value"),
    State("y-label", "value"),
    State("df_records", "data"),
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
        dataset = plot_config.get("dataset", None)
        figure_type = plot_config.get("figure_type", None)
        x_axis = plot_config.get("x_axis", None)
        y_axis = plot_config.get("y_axis", None)
        groupby = plot_config.get("groupby", None)
        display = plot_config.get("display", None)
        agg_type = plot_config.get("agg_type", None)
        agg_col = plot_config.get("agg_col", None)
        if display == "None" or not dataset or \
                (not (x_axis and y_axis) and not (agg_type and groupby and agg_col)):
            continue
        df = pd.DataFrame.from_records(df_records[dataset])
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
    Output("plot-fig", "figure", allow_duplicate=True),
    Input("title", "value"),
    Input("x-label", "value"),
    Input("y-label", "value"),
    prevent_initial_call=True
)
def patch_plot_figure_label(title, x_label, y_label):
    trigger_info = ctx.triggered[0]["prop_id"].split(".")[0]
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

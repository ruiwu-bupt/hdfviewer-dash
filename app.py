from dash import Dash, dcc, html
import dash_bootstrap_components as dbc


from components.table import tables_tab, h5_warning_modal
from components.plot import plot_tab


app = Dash(__name__, title="hdfplotter",
           external_stylesheets=[dbc.themes.BOOTSTRAP])

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
        id='upload_data',
        children=html.Div([
            '拖拽或 ',
            html.A('选择文件(*.hdf5 *.h5)')
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
    ),
    dcc.Store(id="attrs", data={}),
    dcc.Store(id="df_records"),
    h5_warning_modal,
    html.Div([main_tabs])

])


if __name__ == '__main__':

    app.run(debug=True)

from dash import Dash, dcc, html, dash_table, Input, Output
from dash import State, callback, ctx, Patch, no_update, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc


from components.table import tables_tab
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
    dcc.Store(id="attrs", data={}),
    dcc.Store(id="df_records"),
    html.Div([main_tabs])

])


if __name__ == '__main__':

    app.run(debug=True)

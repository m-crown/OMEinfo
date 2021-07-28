import base64
import datetime
import io
import plotly.graph_objs as go
import plotly.express as px
import cufflinks as cf
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc

import pandas as pd

from convert_geoloc_to_rurality import convert_projection, get_rurality

external_stylesheets = [dbc.themes.GRID, 'https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}

app.layout = html.Div(
    [
        dbc.Row([
            dbc.Col(html.H1("OME.info : Geographical metadata generator"))
        ]),
        dbc.Row(
            dbc.Col(dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ',
                html.A('Select Files')]),
                style={
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                    },
                # Allow multiple files to be uploaded
                multiple=True))),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='Sample_Location')),
                dbc.Col(html.Div(id='output-data-upload'))
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='Rurality_bar')),
                dbc.Col(dcc.Graph(id='Rurality_bar2'))
            ]
        ),
        dcc.Store(id="df_store")
])
def parse_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    df = get_rurality(df, "rurality")
    return df

@app.callback(Output('df_store', 'data'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ],
            prevent_initial_call=True)
def compute_dataframe(contents, filename):
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df['Rurality'] = df['Rurality'].astype('category')
    return df

@app.callback(Output('Sample_Location', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ],
            prevent_initial_call=True)
def update_map(contents, filename):
    fig = {
        'layout': go.Layout(
            #plot_bgcolor=colors["graphBackground"],
            #paper_bgcolor=colors["graphBackground"]
            )
    }
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df['Rurality'] = df['Rurality'].astype('category')
        #df = df.set_index(df.columns[0])
        fig = px.scatter_geo(df,
                    lat=df["Latitude"],
                    lon=df["Longitude"],
                    hover_name="Sample",
                    color = "Rurality")
    return fig

@app.callback(Output('Rurality_bar', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ],
            prevent_initial_call=True)
def update_bar(contents, filename):
    fig = {
        'layout': go.Layout(
            #plot_bgcolor=colors["graphBackground"],
            #paper_bgcolor=colors["graphBackground"]
            )
    }
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df['Rurality'] = df['Rurality'].astype('category')
        fig = px.bar(df,
                    x=df["Rurality"],
                    hover_name="Sample")
        fig.update_xaxes(type = "category")
    return fig

@app.callback(Output('Rurality_bar2', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ],
            prevent_initial_call=True)
def update_bar(contents, filename):
    fig = {
        'layout': go.Layout(
            #plot_bgcolor=colors["graphBackground"],
            #paper_bgcolor=colors["graphBackground"]
            )
    }
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df['Rurality'] = df['Rurality'].astype('category')
        fig = px.bar(df,
                    x=df["Rurality"],
                    hover_name="Sample")
        fig.update_xaxes(type = "category")
    return fig

@app.callback(Output('output-data-upload', 'children'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
def update_table(contents, filename):
    table = html.Div()
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)

        table = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                page_size = 10
            ),
            html.Hr()
        ])
    return table

if __name__ == '__main__':
    app.run_server(debug=True)
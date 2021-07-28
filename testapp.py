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
import numpy as np
from convert_geoloc_to_rurality import convert_projection, get_rurality, get_pop_density, get_koppen
# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
external_stylesheets = [dbc.themes.LITERA] 

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets = external_stylesheets)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

HBBE_LOGO = "/Users/matthewcrown/GitHub/OMEinfo/assets/MICROBIAL_ENVIRONMENTS.png"
HBBE_LOGO_BASE64 = base64.b64encode(open(HBBE_LOGO, 'rb').read()).decode('ascii')
SIDEBAR_STYLE = {
    "background-color": 'transparent',
}
UPLOAD_STYLE = {
    "font-size": 'vi',
}
sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact", style={'margin': '10px'}),
                dbc.NavLink("Page 1", href="/page-1", active="exact", style={'margin': '10px'}),
                dbc.NavLink("Page 2", href="/page-2", active="exact", style={'margin': '10px'}),
            ],
            vertical=True,
            pills=True
        ),
    ],
    style=SIDEBAR_STYLE,
)

navbar = dbc.NavbarSimple(
                children=[
                    html.Img(src='data:image/png;base64,{}'.format(HBBE_LOGO_BASE64), height = "150px"),
                    ],
            brand="OME.info",
            className = "h1",
            brand_href="/",
            color="primary",
            dark=False,
            fluid = True)

index_page = html.Div(
    [   
        dbc.Row(dbc.Col(navbar
        )),
        dbc.Row([
            dbc.Col(sidebar, width = 1),
            dbc.Col([
                html.Div("Welcome to OME.info. SHARE MICROBIOME METADATA, ANONYMOUSLY.", style={'text-align': 'center'})
            ])]),
            dcc.Store(id="df_store")])

page_1_layout = html.Div(
    [   
        dbc.Row(dbc.Col(navbar)),
        dbc.Row([
            dbc.Col(sidebar, width = 1),
            dbc.Col([
                    dbc.Row(
                        dbc.Col(
                            html.Div(children = [
                            dcc.Upload(
                                id='upload-data', 
                                children= html.Div(["Drag and Drop or ", dcc.Link("Select Files", href = "")],
                                style =UPLOAD_STYLE), multiple=True,
                                style={
                                    'width': '75%',
                                    'align-items' : 'center',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px'}
                                    )]),
                                ), justify = "center"),
                    dbc.Row(dbc.Col(html.Div(id ="map_fill", style = {'padding' : '10px'}))),
                    dbc.Row(
                        [
                            dbc.Col(dbc.Card(id='Rurality_bar', color = "primary", outline = True),style={'margin': '10px'}),
                            dbc.Col(dbc.Card(id='Sample_Location', color = "primary", outline = True), style={'margin': '10px'})
                        ]
                    ),
                    dbc.Row(
                        [       
                            dbc.Col(dbc.Card(id='output-data-upload'),style={'margin': '10px'})
                        ],justify = "center")])]),
            dcc.Store(id="df_store")])


def parse_data(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), )
    except Exception as e: #there needs to be a new exception here as this is not displaying a div
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    if 'moll_lat' and 'moll_lon' in df.columns:
        df = get_rurality(df, "rurality")
        df = get_pop_density(df,"pop_density")
        df = get_koppen(df,"koppen")
    else: 
        df = convert_projection(df, "mollweide")
        df = get_rurality(df, "rurality")
        df = get_pop_density(df,"pop_density")
        df = get_koppen(df,"koppen")
    
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
        for col in df.columns:
            if df[col].isna().all(): #using len(col) rather than empty == True because nan gives series a length
                df = df.drop(columns = [col])
        data = df.to_json()
    return data

@app.callback(Output('Sample_Location', 'children'),
            [
                Input('df_store', 'data'),
                Input('map_fill', 'value')
            ],
            prevent_initial_call=True)
def update_map(df, val):
    if df:
        df = pd.read_json(df)
        df['Rurality'] = df['Rurality'].astype('category')
        df['Koppen'] = df['Koppen'].astype('category')
        fig = px.scatter_geo(df,
                    lat=df["Latitude"],
                    lon=df["Longitude"],
                    hover_name="Sample",
                    color = val)
        fig.update_layout(go.Layout(
            paper_bgcolor = 'rgba(0, 0, 0, 0)',
            plot_bgcolor ='rgba(0, 0, 0, 0)'))        
        map_output = dcc.Graph(figure=fig, style={'width': '75vh', 'height': '50vh'})
        comment = ""
        if val == "Koppen":
            comment = html.P("Koppen climate classification measured according to Wood et. al (2018)", className="card-text",)
        elif val == "Rurality":
            comment = html.P("Rurality measured according to GHS-SMOD", className="card-text",)
        card_content = [
            dbc.CardHeader("Sample Location"),
            dbc.CardBody(
                [
                    map_output
                ]
                ),
            dbc.CardFooter(comment)
            ]
    else:
        card_content = html.Div()
    return card_content

@app.callback(Output('Rurality_bar', 'children'),
            [
                Input('df_store', 'data'),
                Input('map_fill', 'value')
            ],
            prevent_initial_call=True)
def update_bar(df, val):
    if df:
        df = pd.read_json(df)
        df['Rurality'] = df['Rurality'].astype('category')
        fig = px.histogram(df,
                    x=df[val],
                    hover_name="Sample",
                    color = df[val])
        fig.update_xaxes(type = "category")
        fig.update_layout(go.Layout(
            paper_bgcolor = 'rgba(0, 0, 0, 0)',
            plot_bgcolor ='rgba(0, 0, 0, 0)'))
        graph = dcc.Graph(figure=fig, style={'width': '75vh', 'height': '50vh'})
        if val == "Koppen":
            comment = html.P("Koppen climate classification measured according to Wood et. al (2018)",className="card-text",)
        elif val == "Rurality":
            comment = html.P("Rurality measured according to GHS-SMOD",className="card-text",)
        card_content = [
            dbc.CardHeader("Breakdown of metadata feature"),
            dbc.CardBody(
                [
                    graph
                ]
                ),
            dbc.CardFooter(comment)
            ]
    else:
        card_content = html.Div()
    return card_content

@app.callback(Output('output-data-upload', 'children'),
            [
                Input('df_store', 'data')
            ])
def update_table(df):
    table = html.Div()
    if df:
        df = pd.read_json(df)
        df = df.drop(columns = ["moll_lat", "moll_lon"])
        comment = "+____+"
        table = dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i, "deletable": True} for i in df.columns],
                filter_action = "native",
                page_size = 10,
                export_format="csv", 
                style_cell = {'textAlign' : 'left', 'backgroundColor': 'rgba(0, 0, 0, 0)'},
                style_header = {'textAlign' : 'left', 'backgroundColor': 'rgba(0, 0, 0, 0)'})
        card_content = [
            dbc.CardHeader("Breakdown of metadata feature"),
            dbc.CardBody(
                [
                    table,
                    comment
                ]
                ),
            ]
    else:
        card_content = html.Div()
    return card_content

@app.callback(Output('map_fill', 'children'),
            [
                Input('df_store', 'data')
            ])
def populate_dropdown(df):
    if df:
        dropdown = dcc.Dropdown(
                    id='map_fill',
                    options=[{"label": "Rurality", "value": "Rurality"}, {"label":"Koppen", "value": "Koppen"}],
                    value='Koppen')
        return dropdown

page_2_layout = html.Div(
    [   
        dbc.Row(dbc.Col(navbar)),
        dbc.Row([
            dbc.Col(sidebar, width = 1),
            dbc.Col([
                    dbc.Row(dbc.Col([
                        html.H1('Page 2'),
                        html.Div("PLACEHOLDER PAGE FOR SEARCH FEATURE"),
                        html.Div(id='page-2-content'),
                        html.Br(),
                        dcc.Link('Go to Page 1', href='/page-1'),
                        html.Br(),
                        dcc.Link('Go back to home', href='/')]))])])])
    

@app.callback(dash.dependencies.Output('page-2-content', 'children'),
              [dash.dependencies.Input('page-2-radios', 'value')])
def page_2_radios(value):
    return 'You have selected "{}"'.format(value)


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run_server(debug=True)
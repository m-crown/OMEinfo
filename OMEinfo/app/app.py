import base64
import datetime
import io
import plotly.graph_objs as go
import plotly.express as px

import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from dash import dash_table
import dash_bootstrap_components as dbc

import pandas as pd
import numpy as np
from convert_geoloc_to_rurality import convert_projection, get_s3_point_data

# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/styles.css"] 

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets = external_stylesheets)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

LOGO = "assets/logo.png"
LOGO_BASE64 = base64.b64encode(open(LOGO, 'rb').read()).decode('ascii')
SIDEBAR_STYLE = {
    "background-color": 'transparent',
}
UPLOAD_STYLE = {
    "font-size": 'vi',
}

logo_image = html.Img(src='data:image/png;base64,{}'.format(LOGO_BASE64), height='150px')
brand_component = html.Div(logo_image, className='navbar-brand')

navbar = dbc.NavbarSimple(
    children = [dbc.NavLink("Analyse", href="/analyse", active="exact", style={'margin': '10px'})],
    brand=brand_component,
    brand_href = "/",
    className="h1",
    color="#dee0dc",
    dark=False,
    fluid=True
)

index_page = html.Div(
    [   
        dbc.Row(dbc.Col(navbar)),
        dbc.Row([
            dbc.Col([dbc.Card(
                html.Div([
                    html.P("Microbiome classification studies increasingly associate geographical features like rurality and climate type with microbiomes. However, microbiologists and bioinformaticians often struggle to access and integrate rich geographical metadata from sources like GeoTIFs. Inconsistent definitions of rurality, for example, can hinder cross-study comparisons. \nTo address this, we present OMEInfo, a Python-based tool that automates the retrieval of consistent geographical metadata like Koppen climate classification, rurality, population density, and CO2 emissions from user-provided location data.\n OMEInfo leverages open data sources like the Global Human Settlement Layer (GHSL), Koppen climate classification models and ODIAC, to ensure metadata accuracy and provenance.\n OMEInfo's Dash web application enables users to visualize their data and metadata on a map and a histogram. The tool is available as a Docker container, providing a portable, lightweight solution for researchers.\n Key features of OMEInfo include:"),
                    html.Ul([
                        html.Li("Standardized metadata retrieval approach"),
                        html.Li("Incorporating FAIR and OPEN data principles"),
                        html.Li("Promoting reproducibility and cross-study comparisons in microbiome research"),
                    ]),
                    html.P("As the field continues to explore the relationship between microbiomes and geographical features, tools like OMEInfo will prove vital in developing a robust, accurate, and interconnected understanding of these complex interactions.\n If you use OMEinfo to obtain geographic metadata, please cite:"),
                    html.Ul([
                        html.Li("Fossil Fuel CO2 data: Tomohiro Oda, Shamil Maksyutov (2015), ODIAC Fossil Fuel CO2 Emissions Dataset (Version name : ODIAC2020b), Center for Global Environmental Research, National Institute for Environmental Studies, doi:10.17595/20170411.001. (Reference date : 2023/04/20)"),
                        html.Li("Koppen-Geiger Climate Classification: Beck, H., Zimmermann, N., McVicar, T. et al. Present and future Köppen-Geiger climate classification maps at 1-km resolution. Sci Data 5, 180214 (2018). https://doi.org/10.1038/sdata.2018.214"),
                        html.Li("Population Density: Schiavina, Marcello; Freire, Sergio; MacManus, Kytt (2019): GHS population grid multitemporal (1975, 1990, 2000, 2015) R2019A. European Commission, Joint Research Centre (JRC) DOI: 10.2905/42E8BE89-54FF-464E-BE7B-BF9E64DA5218"),
                        html.Li("Rurality: Pesaresi, Martino; Florczyk, Aneta; Schiavina, Marcello; Melchiorri, Michele; Maffenini, Luca (2019): GHS settlement grid, updated and refined REGIO model 2014 in application to GHS-BUILT R2018A and GHS-POP R2019A, multitemporal (1975-1990-2000-2015), R2019A. European Commission, Joint Research Centre (JRC) DOI: 10.2905/42E8BE89-54FF-464E-BE7B-BF9E64DA5218")
                    ]),
                ], style={'text-align': 'center'})
            )])
        ]),
        dcc.Store(id="df_store")
    ]
)


page_1_layout = html.Div(
    [   
        dbc.Row(dbc.Col(navbar)),
        dbc.Row([
            dbc.Col([
                    dbc.Row(
                        dbc.Col(
                            html.Div(children = [
                            dcc.Upload(
                                id='upload-data', 
                                children= html.Div(["Drag and Drop or ", dcc.Link("Select Files", href = "")],
                                style =UPLOAD_STYLE), multiple=True,
                                style={
                                    
                                    'align-items' : 'center',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px 0'}
                                    )]),
                                style={'margin': '10px'}), justify = "center"),
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
    s3_bucket = 'cloudgeotiffbucket'
    s3_key_rur_pop_kop = 'rurpopkop_v1_cog.tif'
    s3_key_co2 = 'co2_v1_cog.tif'
    s3_region = 'eu-north-1'
    s3_url_rur_pop_kop = f"https://{s3_bucket}.s3.{s3_region}.amazonaws.com/{s3_key_rur_pop_kop}"
    s3_url_co2 = f"https://{s3_bucket}.s3.{s3_region}.amazonaws.com/{s3_key_co2}"
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
        df = get_s3_point_data(df, s3_url_rur_pop_kop, "rur_pop_kop", coord_projection="ESRI:54009")
        df = get_s3_point_data(df, s3_url_co2, "co2", coord_projection="ESRI:54009")
    else: 
        df = convert_projection(df, "mollweide")
        df = get_s3_point_data(df, s3_url_rur_pop_kop, "rur_pop_kop", coord_projection="ESRI:54009")
        df = get_s3_point_data(df, s3_url_co2,"co2", coord_projection="ESRI:54009")
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
        elif val == "Population Density":
            comment = html.P("Pop Dens GHS-SMOD", className="card-text",)
        elif val == "CO2 emissions":
            comment = html.P("ODIAC Fossil Fuel Co2 Emissions", className="card-text",)
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
        if val != "Population Density":
            fig = px.histogram(df,
                        x=df[val],
                        hover_name="Sample",
                        color = df[val])
        if val == "Population Density":
            fig = px.histogram(df,
                        x=df[val],
                        hover_name="Sample")
        if val == "Rurality" or val == "Koppen":
            fig.update_xaxes(type = "category")
        fig.update_layout(go.Layout(
            paper_bgcolor = 'rgba(0, 0, 0, 0)',
            plot_bgcolor ='rgba(0, 0, 0, 0)'))
        graph = dcc.Graph(figure=fig, style={'width': '75vh', 'height': '50vh'})
        if val == "Koppen":
            comment = html.P("Koppen-Geiger climate classification measured according to Wood et. al (2018)",className="card-text",)
        elif val == "Rurality":
            comment = html.P("Rurality measured according to GHS-SMOD",className="card-text",)
        elif val == "Population Density":
            comment = html.P("Pop Dens GHS",className="card-text",)
        elif val == "CO2 emissions":
            comment = html.P("ODIAC Fossil Fuel Co2 Emissions", className="card-text",)
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
                    options=[{"label": "Rurality", "value": "Rurality"}, {"label":"Koppen", "value": "Koppen"}, {"label": "Population Density", "value": "Population Density"}, {"label" : "CO2 Emissions", "value" : "CO2 emissions"}],
                    value='Koppen')
        return dropdown

# page_2_layout = html.Div(
#     [   
#         dbc.Row(dbc.Col(navbar)),
#         dbc.Row([
#             dbc.Col([
#                     dbc.Row(dbc.Col([
#                         html.H1('Page 2'),
#                         html.Div("PLACEHOLDER PAGE FOR SEARCH FEATURE"),
#                         html.Div(id='page-2-content'),
#                         html.Br(),
#                         dcc.Link('Go to Page 1', href='/page-1'),
#                         html.Br(),
#                         dcc.Link('Go back to home', href='/')]))])])])
    

# @app.callback(dash.dependencies.Output('page-2-content', 'children'),
#               [dash.dependencies.Input('page-2-radios', 'value')])
# def page_2_radios(value):
#     return 'You have selected "{}"'.format(value)


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/analyse':
        return page_1_layout
    # elif pathname == '/page-2':
    #     return page_2_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)

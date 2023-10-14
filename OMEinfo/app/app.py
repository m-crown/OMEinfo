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
import requests

import os
from omeinfo import get_s3_point_data

import dash_loading_spinners as dls

# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/dbc.min.css"] 

APP_VERSION = "0.1.0"
LOGO_BASE64 = base64.b64encode(open("assets/logos/logo_brand.png", 'rb').read()).decode('ascii')
OMEINFO_DATA_VERSION = os.environ.get('OMEINFO_VERSION', "2.0.0")

version_info = {"1.0.0" : {"data_list_group" : dbc.ListGroup([dbc.ListGroupItem("Open-source Data Inventory for Anthropogenic CO2"), dbc.ListGroupItem("Global Human Settlement Layer (European Commission)"), dbc.ListGroupItem("Sentinel 5p Satellite (European Space Agency)"), dbc.ListGroupItem("Beck et al. (2018)")]),
                           "data_info" : {"Rurality" : {"comment" : "Rurality is determined using the Global Human Settlement Layer, and provides a global coverage for rurality, in line with the UN’s Global Definition of Cities and Rural Areas, at 1km resolution.", "source" : '<a href="https://ghsl.jrc.ec.europa.eu/">Global Human Settlement Layer (R2019A)</a>', "value" : "rurality", "title": "Rurality", "filepath": "assets/rurality.html"},
                                          "Population Density" : {"comment" : "Population Density is determined using the Global Human Settlement Layer, and provides a global coverage for population density. In OMEinfo v1 dataset, the density is per 1km", "source" : '<a href="https://ghsl.jrc.ec.europa.eu/">Global Human Settlement Layer (R2019A)</a>', "value" : "pop_density", "title": "Population Density", "filepath": "assets/pop_density.html"},
                                          "Fossil Fuel CO2 emissions" : {"comment" : "Fossil fuel CO2 emissions are derived from the ODIAC data product, originally developed from the GOSAT project, and provide an indication of CO2 emissions from fossil fuel combustion, cement production and gas flaring, at a 1km resolution.", "source" : '<a href="https://odiac.org/index.html">ODIAC</a>', "value" : "co2", "title" : "Fossil Fuel CO2 Emissions", "filepath": "assets/mean-co2.html"},
                                          "Tropospheric Nitrogen Dioxide Emissions" : {"comment" : "Tropospheric NO2 concentration is determined using the Copernicus Sentinel 5p satellite. Current data is derived from an annual mean tropospheric vertical column of NO2 for 2022, at a resolution of 1113.2m per pixel.", "source" : '<a href="https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_NO2#bands">Sentinel S5P</a>', "value" : "mean_no2", "title" : "Tropospheric Nitrogen Dioxide Emissions", "filepath": "assets/mean_no2.html"}, 
                                         
                                          "Koppen Geiger" : {"comment" : "Koppen-Geiger climate classification is determined using the model shared in Beck et al. (2018). This model provides an updated classification separated into 30 subtypes.", "source" : '<a href="https://www.nature.com/articles/sdata2018214">Beck et al. (2018)</a>', "value" : "koppen_geiger", "title": "Koppen-Geiger climate classification", "filepath": "assets/koppen-geiger.html"}}},
                            "data_bibtex" : "https://raw.githubusercontent.com/m-crown/OMEinfo/main/citations/v1_citations.bib",
                            "version_output_filename" : "omeinfo_v1_citations.bib",
                "2.0.0" : {"data_list_group" : dbc.ListGroup([dbc.ListGroupItem("Open-source Data Inventory for Anthropogenic CO2"), dbc.ListGroupItem("Global Human Settlement Layer (European Commission)"), dbc.ListGroupItem("Sentinel 5p Satellite (European Space Agency)"), dbc.ListGroupItem("Beck et al. (2018)"), dbc.ListGroupItem("NASA Socioeconomic Data and Applications Center (SEDAC)")]), 
                           "data_info" : {"Rurality" : {"comment" : "Rurality is determined using the Global Human Settlement Layer, and provides a global coverage for rurality, in line with the UN’s Global Definition of Cities and Rural Areas, at 1km resolution.", "source" : '<a href="https://ghsl.jrc.ec.europa.eu/">Global Human Settlement Layer (R2019A)</a>', "value" : "rurality", "title": "Rurality", "filepath": "assets/rurality.html"},
                                          "Population Density" : {"comment" : "Population Density is determined using the Global Human Settlement Layer, and provides a global coverage for population density. In OMEinfo v2 dataset, the density is per 1km", "source" : '<a href="https://ghsl.jrc.ec.europa.eu/">Global Human Settlement Layer (R2019A)</a>', "value" : "pop_density", "title": "Population Density", "filepath": "assets/pop_density.html"},
                                          "Fossil Fuel CO2 emissions" : {"comment" : "Fossil fuel CO2 emissions are derived from the ODIAC data product, originally developed from the GOSAT project, and provide an indication of CO2 emissions from fossil fuel combustion, cement production and gas flaring, at a 1km resolution.", "source" : '<a href="https://odiac.org/index.html">ODIAC</a>', "value" : "co2", "title" : "Fossil Fuel CO2 Emissions", "filepath": "assets/mean-co2.html"},
                                          "Tropospheric Nitrogen Dioxide Emissions" : {"comment" : "Tropospheric NO2 concentration is determined using the Copernicus Sentinel 5p satellite. Current data is derived from an annual mean tropospheric vertical column of NO2 for 2022, at a resolution of 1113.2m per pixel.", "source" : '<a href="https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_NO2#bands">Sentinel S5P</a>', "value" : "mean_no2", "title" : "Tropospheric Nitrogen Dioxide Emissions", "filepath": "assets/mean_no2.html"}, 
                                          "Relative Deprivation" : {"comment" : "Relative Deprivation", "source" : '<a href="https://sedac.ciesin.columbia.edu/data/set/povmap-grdi-v1">SEDAC</a>', "value" : "rel_dep", "title" : "Relative Deprivation", "filepath": ""},
                                          "Koppen Geiger" : {"comment" : "Koppen-Geiger climate classification is determined using the model shared in Beck et al. (2018). This model provides an updated classification separated into 30 subtypes.", "source" : '<a href="https://www.nature.com/articles/sdata2018214">Beck et al. (2018)</a>', "value" : "koppen_geiger", "title": "Koppen-Geiger climate classification", "filepath": "assets/koppen-geiger.html"}}},
                            "data_bibtex" : "https://raw.githubusercontent.com/m-crown/OMEinfo/main/citations/v2_citations.bib",
                            "version_output_filename" : "omeinfo_v2_citations.bib"}

logo_image = html.Img(src='data:image/png;base64,{}'.format(LOGO_BASE64), height='50vh')
brand_component = html.Div(logo_image, className='navbar-brand')

navbar = html.Div(dbc.NavbarSimple(
    children = [dbc.NavLink("Home", href="/", active="exact", style={'margin': '10px'}), dbc.NavLink("Analyse", href="/analyse", active="exact", style={'margin': '10px'}), dbc.NavLink("Explore", href="/explore", active="exact", style={'margin': '10px'})],
    brand=brand_component,
    brand_href = "/",
    className="h4",
    color="#dee0dc",
    dark=False,
    fluid=True,
    style = {"width" : True}
))

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets = external_stylesheets)

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', style = {'height': '100vh','overflowY': 'auto'})
])

version_card = dbc.Card(
    [
        dbc.CardHeader("Version Information"),
        dbc.CardBody(
            [
                html.P(f'OMEinfo Version: v{APP_VERSION}', style = {'padding': '0px'}, className="card-text"),
                html.P(f'Datasource Version: v{OMEINFO_DATA_VERSION}', style = {'padding': '0px'}, className="card-text") 
            ]
        ),
    ],
    style={"width": True, 'padding': '10px 10px 10px 10px'},
)

info_card = dbc.Card(
    [
        dbc.CardImg(src="assets/logos/logo.png", top=True, style={'width': '10%', 'margin': 'auto'}),
        dbc.CardBody(
            [
                html.H4("Welcome to OMEInfo!", className="card-title"),
                html.P(
                    "OMEInfo is a tool to help biological sciences researchers enhance their metadata through integration of global scale geographical data",
                    "from open data source, including rurality, population density, anthropengic CO2 emissions and Koppen-Geiger climate type.",
                    className="card-text",
                ),
                html.P(
                    "To get started click the 'Analyse' button or navigate to the 'Analyse' page above and upload your metadata file, including latitude and longitude columns in decimal degrees for each sample.",
                    "OMEInfo will then analyse your metadata and return a new file with additional columns containing the geographical data.",
                    className="card-text",
                ),
                dbc.Button("Analyse", href = "/analyse" , color="primary"),
            ]
        ),
    ],
    style={"width": True},
)

info_accordion = dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    html.P("OMEinfo runs in the web, and all it requires is a metadata form in CSV format with sample names and geolocation information.")
                ],
                title="Simple and Easy to Use",
            ),
            dbc.AccordionItem(
                [
                    html.P("GeoTIFF files can be large and unwieldly to process. OMEinfo uses cloud based GeoTIFFs to process data quickly and efficiently.")
                ],
                title="Cloud Based GeoTIFF Processing",
            ),
            dbc.AccordionItem(
                [
                    html.P("Data used in OMEinfo is versioned and citable, and all data sources are referenced in the 'Explore' section of the website, helping to make research more reproducible.")
                ],
                title="Fair and Open Data Sharing",
            ),
            dbc.AccordionItem(
                [
                    html.P("All data is processed locally, with no personally identifiable information being transmitted.")
                ],
                title="Private and Secure",
            ),
        ],
    )

info_carousel = dbc.Carousel(
    items=[
        {
            "key": "1",
            "src": "assets/carousel_images/Image002.png",
        },
        {
            "key": "2",
            "src": "assets/carousel_images/Image003.png",
        },
        {
            "key": "3",
            "src": "assets/carousel_images/Image004.png",
        },
        {
            "key": "4",
            "src": "assets/carousel_images/Image005.png",
        },
        {
            "key": "5",
            "src": "assets/carousel_images/Image006.png",
        },
        {
            "key": "6",
            "src": "assets/carousel_images/Image001.png",
        },
    ],
    controls=True,
    indicators=True,
    variant = "dark"
)

index_page =  [   
        dbc.Row(dbc.Col(navbar, width = True)),
        dbc.Row(dbc.Col(info_card, style={'text-align': 'center', 'margin': '10px'}, width = True), justify = "center"),
        dbc.Row([dbc.Col(info_carousel, style={'textAlign': 'center', 'margin': '10px'}),dbc.Col(info_accordion, style={'textAlign': 'center', 'margin': '10px'})], align = "center", justify = "center"),
        dbc.Row(dbc.Col(version_card, style={'textAlign': 'center', 'margin': '10px 10px 10px 10px'}, width = True), justify = "center")
    ]


tab1_content = dbc.Card(id='bar', outline = True)
tab2_content = dbc.Card(id='Sample_Location', outline = True)
tab3_content = dbc.Card(id='output-data-upload')

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Graph"),
        dbc.Tab(tab2_content, label="Map"),
        dbc.Tab(tab3_content, label="Table"),
    ])

page_1_layout = [dbc.Row(dbc.Col(navbar)),
            dbc.Row(
                dbc.Col(
                    dcc.Upload(
                        id='upload-data', 
                        children= html.Div(["Drag and Drop or ", dcc.Link("Select Files", href = "")], id = "upload-link",
                        style ={"font-size": 'vi'}), multiple=True,
                        style={
                            'align-items' : 'center',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px 0'}
                            )), justify = "center"),
                        
            dbc.Row(dbc.Col(html.Div(id ="map_fill", style = {'padding' : '10px'}))),
            dbc.Row(
                dbc.Col(
                    dbc.Spinner(
                        id="loading-data",  # Add an ID to the Loading component
                        fullscreen = False,
                        children = html.Div(
                            [
                                dbc.Row(dbc.Col(html.Div(tabs, id='tabs', style={'display': 'none'}), width = True), justify = "center"),
                                dbc.Row(
                                [
                                    dbc.Col(dbc.Button("Download Annotated Metadata", id="download_button_df", class_name="mx-auto", style={'align-items': 'center','display': 'none'}), align = "center", width = 4),
                                    dbc.Col(dbc.Button("Download BibTeX", id="download_button", class_name="mx-auto", style={'align-items': 'center', 'display': 'none'}), align = "center", width = 4)
                                ], justify="center"),
                            dcc.Download(id="download_df"), 
                            dcc.Download(id="download")
                            ])),
                        style={'padding': '10px 10px 10px 10px'}, width = True), justify = "center"),
            
            dbc.Row(dbc.Col(version_card, style={'textAlign': 'center', 'margin': '10px'}, width = True), justify = "center"),
            dcc.Store(id="df_store")
        ]

data_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Data exploration", className="card-title"),
                html.P(
                    "OMEinfo is enabled through open access geographic data sharing. The creators are grateful to the following organisations for their commitment to open data sharing:",
                    className="card-text", style = {"text-align": "left"}
                ),
                version_info[OMEINFO_DATA_VERSION]["data_list_group"],
                html.P(
                    f"""Analysis performed with this version of the OMEinfo tool uses OMEinfo data set v{OMEINFO_DATA_VERSION}, a collection of GIS data sources. 
                    If you use data derived from OMEinfo, please use the following bibtex file to credit OMEinfo and the data source authors:""",
                    className="card-text", style = {"text-align": "left"}
                ),
                dbc.Button("Download BibTeX", id = "download_button"),
                dcc.Download(id="download")
            ]
        ),
    ],
    style={"width": True},
)

explore_page_layout = [dbc.Row([dbc.Col(navbar, style={'textAlign': 'center', 'margin': '10px'})], align = "center", justify = "center"),
     dbc.Row([
        dbc.Col([dbc.Card(
                    [
                        dbc.CardHeader(id = "output-iframe-title"),
                        dbc.CardBody(
                            [
                                html.Iframe(id='output-iframe', style={'width': '90%', 'height': '90%'}),
                                dcc.Dropdown(
                                    id='dropdown',
                                    options=
                                        #need to make this into a loop to build dictionaries?
                                        [{"label": key, "value": key} for key in version_info[OMEINFO_DATA_VERSION]["data_info"]]
                                    ,
                                    value='Tropospheric Nitrogen Dioxide Emissions',
                                    className='mx-auto'
                                ),
                            ],
                            className="text-center"
                        )
                    ],
                    style={'height': '50vh', 'margin': '10px'},
                )]),
        dbc.Col([
            dbc.Row([
            dbc.Col([
                html.Div(id = "output-card", style = {'padding' : '10px'})
        ])]),
            dbc.Row([ 
            dbc.Col(data_card, style={'text-align': 'center', 'margin': '10px'}, width = True)], justify = "center")
     ])
    ]),
    dbc.Row(dbc.Col(version_card, style={'textAlign': 'center', 'margin': '10px'}, width = True), justify = "center")]

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
    if 'latitude' and 'longitude' in df.columns:
        rurality_definitions = pd.read_csv("rurality_legend.txt", sep = "\t")
        kg_definitions = pd.read_csv("kg_legend.txt", sep = "\t")
        id_to_rurality = rurality_definitions.set_index('id')['definition'].to_dict()
        id_to_kg = kg_definitions.set_index('id')['definition'].to_dict()
        df = get_s3_point_data(df, OMEINFO_DATA_VERSION, rurality_def = id_to_rurality, kg_def = id_to_kg, coord_projection="EPSG:4326")
    return df

@app.callback(
    [
        Output('df_store', 'data'),
        Output('loading-data', 'is_loading'),
        Output('tabs', 'style'),
        Output('download_button_df', 'style'),
        Output('upload-data', 'style'),
        Output('upload-link', 'style'),
        Output('download_button', 'style')
    ],
    [
        Input('upload-data', 'contents'),
        Input('upload-data', 'filename')
    ],
    prevent_initial_call=True
)
def compute_dataframe(contents, filename):
    # Initialize is_loading to False
    is_loading = False

    if contents:
        contents = contents[0]
        filename = filename[0]
        
        # Set is_loading to True while processing
        is_loading = True

        df = parse_data(contents, filename)
        df['Rurality'] = df['Rurality'].astype('category')
        for col in df.columns:
            if df[col].isna().all():
                df = df.drop(columns=[col])
        data = df.to_json()
        
        # Set is_loading back to False when done
        is_loading = False

    # Conditionally set style properties to make tabs and button visible
        tabs_style = {'display': 'block', 'padding': '10px'}
        button_style = {'display': 'block', 'padding': '10px', 'text-align': 'center', 'justify-content': 'center', 'align-items': 'center'}
        upload_data_style = {'display': 'none'}
        download_button_style = {'display': 'block', 'padding': '10px', 'text-align': 'center', 'justify-content': 'center', 'align-items': 'center'}

    else:
        data = dash.no_update  # No data update, keep the previous value
        tabs_style = {'display': 'none'}  # Hide tabs
        button_style = {'display': 'none'}  # Hide button

    return data, is_loading, tabs_style, button_style, upload_data_style, upload_data_style, download_button_style

@app.callback(Output('Sample_Location', 'children'),
            [
                Input('df_store', 'data'),
                Input('map_fill', 'value')
            ],
            prevent_initial_call=True)
def update_map(df, val):
    if df and not val == None:

        comment = version_info[OMEINFO_DATA_VERSION]["data_info"][val]["comment"]

        if val == "Koppen Geiger":
            val = "koppen_geiger_id"
        elif val == "Rurality":
            val = "rurality_id"

        df = pd.read_json(df)
        df['Rurality'] = df['Rurality'].astype('category')
        df['Koppen Geiger'] = df['Koppen Geiger'].astype('category')
        hover_text = df[[col for col in df.columns if col not in ['latitude', 'longitude', 'rurality_id', 'koppen_geiger_id']]].apply(lambda row: '<br>'.join([f"{col}: {row[col]}" for col in row.index]), axis=1)
        
        fig = go.Figure(go.Scattermapbox(
            lat=df["latitude"],
            lon=df["longitude"],
            hovertext=hover_text,
            marker=dict(
                size=10,  # Adjust the size of the markers
                color=df[val],
            ),
        ))

        fig.update_layout(
            mapbox=dict(
                style="open-street-map",  # Choose the desired mapbox style
                center=dict(lat=df["latitude"].head(1)[0], lon=df["longitude"].head(1)[0]),  # Set the initial center of the map
                zoom=2  # Set the initial zoom level of the map
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            autosize=True,
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)'
        )

        map_output = dcc.Graph(figure=fig)

        card_content = [
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

@app.callback(Output('bar', 'children'),
            [
                Input('df_store', 'data'),
                Input('map_fill', 'value')
            ],
            prevent_initial_call=True)
def update_bar(df, val):
    if df and not val == None:
        comment = html.P(version_info[OMEINFO_DATA_VERSION]["data_info"][val]["comment"],className="card-text")

        df = pd.read_json(df)
        df['Rurality'] = df['Rurality'].astype('category')
        if val not in ["Population Density", "Fossil Fuel CO2 emissions", "Tropospheric Nitrogen Dioxide Emissions", "Relative Deprivation"]:
            fig = px.histogram(df,
                        x=df[val],
                        hover_name="sample",
                        color = df[val])
        else:
            fig = px.histogram(df,
                        x=df[val],
                        hover_name="sample")
        if val == "Rurality" or val == "Koppen Geiger":
            fig.update_xaxes(type = "category")
        fig.update_layout(go.Layout(
            paper_bgcolor = 'rgba(0, 0, 0, 0)',
            plot_bgcolor ='rgba(0, 0, 0, 0)'), title=f'{version_info[OMEINFO_DATA_VERSION]["data_info"][val]["title"]}<br>Source: {version_info[OMEINFO_DATA_VERSION]["data_info"][val]["source"]}', showlegend=False)

        scatter_margin = dict(l=0, r=0, t=0, b=0)  # Set the margin values to 0

        graph = dcc.Graph(figure=fig, style={"margin": scatter_margin, "autosize" : True}) #"width": "100%", "height": "100%", 
        card_content = [
            dbc.CardBody(
                [
                    html.Div(graph)
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
        df_display = df.copy()
        df_display = df.drop(columns = ["rurality_id", "koppen_geiger_id"])
        df_display["Tropospheric Nitrogen Dioxide Emissions"] = df_display["Tropospheric Nitrogen Dioxide Emissions"].apply(lambda x: '{:.{}e}'.format(x, 2))
        df_display[["Fossil Fuel CO2 emissions", "Population Density"]] = df_display[["Fossil Fuel CO2 emissions", "Population Density"]].round(2)
        table = dash_table.DataTable(
                data=df_display.to_dict('records'),
                columns=[{'name': i, 'id': i, "deletable": True} for i in df_display.columns],
                filter_action = "none",
                page_size = 8,
                style_cell = {'textAlign' : 'left', 'backgroundColor': 'rgba(0, 0, 0, 0)', 'height': 'auto', 'whiteSpace': 'normal'},
                style_header = {'textAlign' : 'left', 'backgroundColor': 'rgba(0, 0, 0, 0)', 'height': 'auto', 'whiteSpace': 'normal'},
                style_table={'overflowX': 'scroll'})

        card_content = [
            dbc.CardBody(
                [
                    html.Div(table,className = "dbc")
                ]
                )
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
        data_list = [{"label": key, "value": key} for key in version_info[OMEINFO_DATA_VERSION]["data_info"].keys()]
        dropdown = dcc.Dropdown(
                    id='map_fill',
                    options = data_list,
                    value= data_list[0]["value"])
        return dropdown

@app.callback(
    Output("download", "data"),
    Input("download_button", "n_clicks"),
    prevent_initial_call=True,
)
def download(n_clicks):
    url = version_info[OMEINFO_DATA_VERSION]["data_bibtex"]
    filename = version_info[OMEINFO_DATA_VERSION]["version_output_filename"]
    req = requests.get(url)
    req.raise_for_status()  # Confirm that the request was successful
    return dcc.send_bytes(req.content, filename=filename)


@app.callback(
    Output("download_df", "data"),
    Input("download_button_df", "n_clicks"),
    State("df_store", "data"),
    prevent_initial_call=True,
)
def download_df(n_clicks, df):
    df = pd.read_json(df)
    df_download = df.drop(columns = ["rurality_id", "koppen_geiger_id"])
    return dcc.send_data_frame(df_download.to_csv, "annotated_metadata.csv", index = False, header=True, sep=",")

@app.callback(
    Output('output-iframe-title', 'children'),
    Output('output-iframe', 'src'),
    Output('output-card', 'children'),
    Input('dropdown', 'value'))
def update_iframe(value):
    src_title = f"{version_info[OMEINFO_DATA_VERSION]['data_info'][value]['title']} Data Description"
    comment = version_info[OMEINFO_DATA_VERSION]["data_info"][value]["comment"]
    src = version_info[OMEINFO_DATA_VERSION]["data_info"][value]["filepath"]
    card_content = [dbc.Card([
            dbc.CardHeader(src_title),
            dbc.CardBody(
                [
                    html.P(comment)
                ]
            )
        ])]
    
    return src_title, src, card_content

# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/analyse':
        return page_1_layout
    elif pathname == '/explore':
        return explore_page_layout
    elif pathname == "/" or "":
        return index_page
    else:
        return index_page #update to a 404 not found page
    
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
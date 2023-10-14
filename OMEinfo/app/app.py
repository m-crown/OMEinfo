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

LOGO_BASE64 = base64.b64encode(open("assets/logos/logo_no_text.png", 'rb').read()).decode('ascii')
GH_LOGO_BASE64 = base64.b64encode(open("assets/logos/github-mark.png", 'rb').read()).decode('ascii')

logo_image = html.Img(src='data:image/png;base64,{}'.format(LOGO_BASE64), height='50vh')
brand_component = html.Div(logo_image, className='navbar-brand')

navbar = dbc.NavbarSimple(
    children = [dbc.NavLink("Home", href="/", active="exact", style={'margin': '10px'}), dbc.NavLink("Analyse", href="/analyse", active="exact", style={'margin': '10px'}), dbc.NavLink("Explore", href="/explore", active="exact", style={'margin': '10px'})],
    brand=brand_component,
    brand_href = "/",
    className="h4",
    color="#dee0dc",
    dark=False,
    fluid=True,
    style = {"width" : True}
)

footer = dbc.Row([
    dbc.Col(
        html.Div(children = [
            html.P("OMEinfo Version: v0.1", style={'textAlign': 'left'}),
            html.P("Datasource Version: v1", style={'textAlign': 'left'})
            ]), width = True),
    dbc.Col(html.Div(children = [
        html.P("Matt Crown, 2023", style={'textAlign': 'center'})]), width = True),
    dbc.Col(html.Div(children = [
        html.A(
            href="https://github.com/m-crown/OMEinfo",
            target="_blank",
            children=[
                html.Img(
                    src="assets/logos/github-mark.png",
                    alt="GitHub Logo",
                    style={"max-width": "10%", "height": "auto", "padding-top": "10px"})
                    ], className="d-flex justify-content-end align-items-center",
                )
            ]
        ),
        style = {'text-align': 'center', 'margin': '10px'}, width = True)],
    className = "footer",
    style = {"background-color": "#dee0dc"},
    justify="center", align="center") #"position": "fixed", "bottom": "0", "width": True,)

info_card = dbc.Card(
    [
        dbc.CardImg(src="assets/logos/logo.png", top=True, style={'width': '15%', 'margin': 'auto'}),
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
                    html.P("Data used in OMEinfo is versioned and citable, and all data sources are referenced in the 'Data' section of the website, helping to make research more reproducible.")
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

index_page = html.Div(style={'height': '100vh', 'overflowY': 'auto'}, children = 
    [   
        dbc.Row(dbc.Col(navbar, width = True)),
        dbc.Row(dbc.Col(info_card, style={'text-align': 'center', 'margin': '10px'}, width = True), justify = "center"),
        dbc.Row([dbc.Col(info_carousel, style={'textAlign': 'center', 'margin': '10px'}),dbc.Col(info_accordion, style={'textAlign': 'center', 'margin': '10px'})], align = "center", justify = "center"),
        footer
    ])


tab1_content = dbc.Card(id='Rurality_bar', color = "primary", outline = True)
tab2_content = dbc.Card(id='Sample_Location', color = "primary", outline = True)
tab3_content = dbc.Card(id='output-data-upload')

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Graph"),
        dbc.Tab(tab2_content, label="Map"),
        dbc.Tab(tab3_content, label="Table"),
    ]
)

page_1_layout = html.Div(style={'height': '100vh', 'overflowY': 'auto'}, children = 
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
                                style ={"font-size": 'vi'}), multiple=True,
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
                    dbc.Row(dbc.Col( 
                        [
                            tabs,
                            dbc.Button("Download Metadata", id="download_button_df"),
                            dcc.Download(id="download_df")
                        ],
                        style = {'padding' : '10px'})
                    )])]),
            footer,
            dcc.Store(id="df_store")])

data_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Data exploration", className="card-title"),
                html.P(
                    "OMEinfo is enabled through open access geographic data sharing. The creators are grateful to the following organisations for their commitment to open data sharing:",
                    className="card-text",
                ),
                html.Ul(
                    [
                        html.Li("Open-source Data Inventory for Anthropogenic CO2"),
                        html.Li("Global Human Settlement Layer (European Commission)"),
                        html.Li("Sentinel 5p Satellite (European Space Agency)"),
                        html.Li("Beck et al. (2018)"),
                    ], style={"text-align": "centre", "list-style-position": "inside"}
                ),
                html.P(
                    "Analysis performed with this version of the OMEinfo tool uses OMEinfo data set V1, a collection of GIS data sources.",
                    "If you use data derived from OMEinfo, please use the following bibtex file to credit OMEinfo and the data source authors:",
                    className="card-text",
                ),
                dbc.Button("Download bibtex", id = "download_button"),
                dcc.Download(id="download")
            ]
        ),
    ],
    style={"width": True},
)

data_source_info_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Data exploration", className="card-title"),
                html.P(
                    "OMEinfo is enabled through open access geographic data sharing. The creators are grateful to the following organisations for their commitment to open data sharing:",
                    className="card-text",
                ),
                html.Ul(
                    [
                        html.Li("Open-source Data Inventory for Anthropogenic CO2"),
                        html.Li("Global Human Settlement Layer (European Commission)"),
                        html.Li("Sentinel 5p Satellite (European Space Agency)"),
                        html.Li("Beck et al. (2018)"),
                    ], style={"text-align": "centre", "list-style-position": "inside"}
                ),
                html.P(
                    "Analysis performed with this version of the OMEinfo tool uses OMEinfo data set V1, a collection of GIS data sources.",
                    "If you use data derived from OMEinfo, please use the following bibtex file to credit OMEinfo and the data source authors:",
                    className="card-text",
                ),
                dbc.Button("Download bibtex", id = "download_button"),
                dcc.Download(id="download")
            ]
        ),
    ],
    style={"width": True},
)

explore_page_layout = html.Div(style={'height': '100vh'}, children = 
    [dbc.Row([dbc.Col(navbar, style={'textAlign': 'center', 'margin': '10px'})], align = "center", justify = "center"),
     dbc.Row([
        dbc.Col([dbc.Card(
                    [
                        dbc.CardHeader(id = "output-iframe-title"),
                        dbc.CardBody(
                            [
                                html.Iframe(id='output-iframe', style={'width': '90%', 'height': '90%'}),
                                dcc.Dropdown(
                                    id='dropdown',
                                    options=[
                                        {'label': 'Mean NO2', 'value': 'mean_no2'},
                                        {'label': 'Population Density', 'value': 'pop_density'},
                                        {'label': 'Rurality', 'value': "rurality"},
                                        {'label': 'Koppen-Geiger', 'value': "koppen_geiger"},
                                        {'label': 'Mean CO2', 'value': "co2"}
                                    ],
                                    value='mean_no2',
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
    footer])

def parse_data(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    s3_bucket = 'cloudgeotiffbucket'
    s3_key_rur_pop_kop = 'rurpopkop_v1_cog.tif'
    s3_key_co2 = 'co2_v1_cog.tif'
    s3_key_no2 = 'no2_v1_cog.tif'
    s3_region = 'eu-north-1'
    s3_url_rur_pop_kop = f"https://{s3_bucket}.s3.{s3_region}.amazonaws.com/{s3_key_rur_pop_kop}"
    s3_url_co2 = f"https://{s3_bucket}.s3.{s3_region}.amazonaws.com/{s3_key_co2}"
    s3_url_no2 = f"https://{s3_bucket}.s3.{s3_region}.amazonaws.com/{s3_key_no2}"

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
        df = get_s3_point_data(df, s3_url_no2, "no2", coord_projection="ESRI:54009")
    if 'latitude' and 'longitude' in df.columns:
        rurality_definitions = pd.read_csv("rurality_legend.txt", sep = "\t")
        kg_definitions = pd.read_csv("kg_legend.txt", sep = "\t")
        id_to_rurality = rurality_definitions.set_index('id')['definition'].to_dict()
        id_to_kg = kg_definitions.set_index('id')['definition'].to_dict()
        df = get_s3_point_data(df, OMEINFO_DATA_VERSION, rurality_def = id_to_rurality, kg_def = id_to_kg, coord_projection="EPSG:4326")
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
    if df and not val == None:
        df = pd.read_json(df)
        df['Rurality'] = df['Rurality'].astype('category')
        df['Koppen Geiger'] = df['Koppen Geiger'].astype('category')
        hover_text = df[['Sample', 'Rurality', 'Koppen Geiger']].apply(lambda row: '<br>'.join(row.values.astype(str)), axis=1)
 
        fig = go.Figure(go.Scattermapbox(
            lat=df["Latitude"],
            lon=df["Longitude"],
            hovertext=hover_text,
            marker=dict(
                size=10,  # Adjust the size of the markers
                color=df[val],
            ),
        ))

        fig.update_layout(
            mapbox=dict(
                style="open-street-map",  # Choose the desired mapbox style
                center=dict(lat=df["Latitude"].head(1)[0], lon=df["Longitude"].head(1)[0]),  # Set the initial center of the map
                zoom=2  # Set the initial zoom level of the map
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            autosize=True,
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)'
        )

        if val == "Koppen Geiger":
            comment = html.P("Koppen-Geiger climate classification measured according to Wood et. al (2018)", className="card-text")
        elif val == "Rurality":
            comment = html.P("Rurality measured according to GHS-SMOD", className="card-text")
        elif val == "Population Density":
            comment = html.P("Pop Dens GHS-SMOD", className="card-text")
        elif val == "Fossil Fuel CO2 emissions":
            comment = html.P("ODIAC Fossil Fuel CO2 Emissions", className="card-text")
        elif val == "Tropospheric Nitrogen Dioxide Emissions":
            comment = html.P("Tropospheric Nitrogen Dioxide Emissions", className="card-text")
        else:
            comment = ""

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

@app.callback(Output('Rurality_bar', 'children'),
            [
                Input('df_store', 'data'),
                Input('map_fill', 'value')
            ],
            prevent_initial_call=True)
def update_bar(df, val):
    if df and not val == None:
        df = pd.read_json(df)
        df['Rurality'] = df['Rurality'].astype('category')
        if val not in ["Population Density", "Fossil Fuel CO2 emissions", "Tropospheric Nitrogen Dioxide Emissions"]:
            fig = px.histogram(df,
                        x=df[val],
                        hover_name="Sample",
                        color = df[val])
        else:
            fig = px.histogram(df,
                        x=df[val],
                        hover_name="Sample")
        if val == "Rurality" or val == "Koppen Geiger":
            fig.update_xaxes(type = "category")
        fig.update_layout(go.Layout(
            paper_bgcolor = 'rgba(0, 0, 0, 0)',
            plot_bgcolor ='rgba(0, 0, 0, 0)'))
        
        if val == "Koppen Geiger":
            comment = html.P("Koppen-Geiger climate classification measured according to Wood et. al (2018)",className="card-text",)
            fig.update_layout(title='Koppen-Geiger climate classification<br>Source: <a href="https://www.nature.com/articles/sdata2018214">Beck et al. (2018)</a>')
        elif val == "Rurality":
            comment = html.P("Rurality measured according to GHS-SMOD",className="card-text",)
            fig.update_layout(title='Rurality<br>Source: <a href="https://ghsl.jrc.ec.europa.eu/">Global Human Settlement Layer (R2019A)</a>')
        elif val == "Population Density":
            comment = html.P("Pop Dens GHS",className="card-text",)
            fig.update_layout(title='Population Density<br>Source: <a href="https://ghsl.jrc.ec.europa.eu/">Global Human Settlement Layer (R2019A)</a>')
        elif val == "Fossil Fuel CO2 emissions":
            comment = html.P("ODIAC Fossil Fuel CO2 Emissions", className="card-text",)
            fig.update_layout(title='Fossil Fuel CO2 Emissions<br>Source: <a href="https://odiac.org/index.html">ODIAC</a>')
        elif val == "Tropospheric Nitrogen Dioxide Emissions":
            comment = html.P("Tropospheric Nitrogen Dioxide Emissions", className="card-text",)
            fig.update_layout(title='Tropospheric Nitrogen Dioxide Emissions<br>Source: <a href="https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_NO2#bands">Sentinel S5P</a>')



        scatter_margin = dict(l=0, r=0, t=0, b=0)  # Set the margin values to 0

        graph = dcc.Graph(figure=fig, style={"width": "100%", "height": "100%", "margin": scatter_margin, "autosize" : True})
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
        df = df.drop(columns = ["moll_lat", "moll_lon"])
        table = dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i, "deletable": True} for i in df.columns],
                filter_action = "native",
                page_size = 10,
                style_cell = {'textAlign' : 'left', 'backgroundColor': 'rgba(0, 0, 0, 0)'},
                style_header = {'textAlign' : 'left', 'backgroundColor': 'rgba(0, 0, 0, 0)'})
        
        comment = "Koppen-Geiger climate classification measured according to Wood et. al (2018). Rurality measured according to GHS-SMOD. Pop Dens GHS. ODIAC Fossil Fuel CO2 Emissions. Tropospheric Nitrogen Dioxide Emissions"

        card_content = [
            dbc.CardBody(
                [
                    table
                ]
                ),
            dbc.CardFooter(comment)
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
                    options=[{"label": "Rurality", "value": "Rurality"}, {"label":"Koppen Geiger", "value": "Koppen Geiger"}, {"label": "Population Density", "value": "Population Density"}, {"label" : "Fossil Fuel CO2 Emissions", "value" : "Fossil Fuel CO2 emissions"}, {"label" : "Tropospheric Nitrogen Dioxide Emissions", "value" : "Tropospheric Nitrogen Dioxide Emissions"}],
                    value='Koppen Geiger')
        return dropdown

@app.callback(
    Output("download", "data"),
    Input("download_button", "n_clicks"),
    prevent_initial_call=True,
)
def download(n_clicks):
    url = "https://raw.githubusercontent.com/m-crown/OMEinfo/main/citations/v1_citations.bib"
    req = requests.get(url)
    req.raise_for_status()  # Confirm that the request was successful
    return dcc.send_bytes(req.content, filename="v1_citations.bib")


@app.callback(
    Output("download_df", "data"),
    Input("download_button_df", "n_clicks"),
    State("df_store", "data"),
    prevent_initial_call=True,
)
def download_df(n_clicks, df):
    df = pd.read_json(df)
    df = df.drop(columns = ["moll_lat", "moll_lon"])
    csv_string = df.to_csv(index=False, encoding="utf-8-sig")
    csv_bytes = csv_string.encode("utf-8-sig")
    b64 = base64.b64encode(csv_bytes).decode()
    return dcc.send_data_frame(df.to_csv, "annotated_metadata.csv", header=True, sep=",")

@app.callback(
    Output('output-iframe-title', 'children'),
    Output('output-iframe', 'src'),
    Output('output-card', 'children'),
    Input('dropdown', 'value'))
def update_iframe(value):
    if value == "mean_no2":
        src = 'assets/mean_no2.html'
        src_title = "Mean Tropospheric Nitrogen Dioxide Example Data Visualisation"
        card_content = [dbc.Card([
            dbc.CardHeader("Mean Tropospheric Nitrogen Dioxide Data Description"),
            dbc.CardBody(
                [
                    html.P("Tropospheric NO2 concentration is determined using the Copernicus Sentinel 5p satellite. Current data is derived from an annual mean tropospheric vertical column of NO2 for 2022, at a resolution of 1113.2m per pixel.")
                ]
            )
        ])]
    elif value == "pop_density":
        src = 'assets/pop_density.html'
        src_title = "Population Density Example Data Visualisation"
        card_content = [dbc.Card([
            dbc.CardHeader("Population Density Data Description"),
            dbc.CardBody(
                [
                    html.P("Population density is determined using the Global Human Settlement Layer, and provides a global coverage for population density. In OMEinfo V1 dataset, the density is per 1km.")
                ]
            )
        ])]
    elif value == "rurality":
        src = 'assets/rurality.html'
        src_title = "Rurality Degree Example Data Visualisation"
        card_content = [dbc.Card([
            dbc.CardBody(
                [
                    html.P("Rurality is determined using the Global Human Settlement Layer, and provides a global coverage for rurality, in line with the UN’s Global Definition of Cities and Rural Areas, at 1km resolution.")
                ]
            )
        ])]
    elif value == "koppen_geiger":
        src = 'assets/koppen-geiger.html'
        src_title = "Koppen-Geiger Climate Classification Example Data Visualisation"
        card_content = [dbc.Card([
            dbc.CardHeader("Koppen-Geiger Climate Classification Data Description"),
            dbc.CardBody(
                [
                    html.P("Koppen-Geiger climate classification is determined using the model shared in Beck et al. (2018). This model provides an updated classification separated into 30 subtypes.", className = "card-text")
                ]
            )
        ])]
    elif value == "co2":
        src = 'assets/mean-co2.html'
        src_title = "Fossil fuel CO2 Emissions Example Data Visualisation"
        card_content = [dbc.Card([
            dbc.CardHeader("Fossil fuel CO2 Emissions Example Data Description"),
            dbc.CardBody(
                [
                    html.P("Fossil fuel CO2 emissions are derived from the ODIAC data product, originally developed from the GOSAT project, and provide an indication of CO2 emissions from fossil fuel combustion, cement production and gas flaring, at a 1km resolution.", className = "card-text")
                ]
            )
        ])]
    else:
        src = ""
        src_title = ""
        card_content = html.Div()
    return src_title, src, card_content

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
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
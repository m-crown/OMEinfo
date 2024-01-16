#!/usr/bin/env python3

#should take as input a file and a data packet version? or a local filepath
import argparse
import pandas as pd
import requests
from rio_tiler.io import Reader
import os
from rich.table import Table
from rich.console import Console

import datetime

def get_s3_point_data(df, version, rurality_def, kg_def, coord_projection="EPSG:4326", user_url = None):
    if version == "2.0.0":
        if user_url:
            s3_url = user_url
        else:
            s3_url = "https://figshare.com/ndownloader/files/44053304" #https://cloudgeotiffbucket.s3.eu-north-1.amazonaws.com/omeinfo_v2.tif
        with Reader(s3_url) as cog:
            rurality_values = []
            pop_density_values = []
            koppen_values = []
            pov_values = []
            co2_values = []
            no2_values = []
            error = []
            for _, row in df.iterrows():
                x, y = row["longitude"], row["latitude"]
                # Read pixel values for all bands at coordinates (x, y)
                try:
                    pointdata = cog.point(x, y, coord_crs=coord_projection, indexes=[1, 2, 3, 4, 5, 6])
                    pop_density_values.append(float(pointdata.data[0]))
                    rurality_values.append(int(pointdata.data[1]))
                    koppen_values.append(int(pointdata.data[2]))
                    pov_values.append(int(pointdata.data[3]))
                    co2_values.append(float(pointdata.data[4]))
                    no2_values.append(float(pointdata.data[5]))
                    error.append(None)
                except Exception as e:
                    pop_density_values.append(None)
                    rurality_values.append(None)
                    koppen_values.append(None)
                    pov_values.append(None)
                    co2_values.append(None)
                    no2_values.append(None)
                    error.append(e)
            df["rurality_id"] = rurality_values
            df["Population Density"] = pop_density_values
            df["koppen_geiger_id"] = koppen_values
            df["Relative Deprivation"] = pov_values
            df["Tropospheric Nitrogen Dioxide Emissions"] = no2_values
            df["Fossil Fuel CO2 emissions"] = co2_values
            df["error"] = error
    
    elif version == "1.0.0":
        if user_url:
            user_url = user_url.split(",")
            s3_url_rur_pop_kop = user_url[0]
            s3_url_co2 = user_url[1]
            s3_url_no2 = user_url[2]
        else:
            s3_url_rur_pop_kop = f"https://figshare.com/ndownloader/files/44053298" #https://cloudgeotiffbucket.s3.eu-north-1.amazonaws.com/rurpopkop_v1_cog.tif
            s3_url_co2 = f"https://figshare.com/ndownloader/files/44053301" #https://cloudgeotiffbucket.s3.eu-north-1.amazonaws.com/co2_v1_cog.tif
            s3_url_no2 = f"https://figshare.com/ndownloader/files/44051945" #https://cloudgeotiffbucket.s3.eu-north-1.amazonaws.com/no2_v1_cog.tif
        with Reader(s3_url_rur_pop_kop) as cog:
            rurality_values = []
            pop_density_values = []
            koppen_values = []
            
            for _, row in df.iterrows():
                x, y = row["longitude"], row["latitude"]
                # Read pixel values for all bands at coordinates (x, y)
                pointdata = cog.point(x, y, coord_crs=coord_projection, indexes=[1, 2, 3])
                
                rurality_values.append(int(pointdata.data[0]))
                pop_density_values.append(float(pointdata.data[1]))
                koppen_values.append(int(pointdata.data[2]))
            
            df["rurality_id"] = rurality_values
            df["Population Density"] = pop_density_values
            df["koppen_geiger_id"] = koppen_values
        with Reader(s3_url_co2) as cog:
            co2_values = []
            for _, row in df.iterrows():
                x, y = row["longitude"], row["latitude"]
                # Read pixel values for all bands at coordinates (x, y)
                pointdata = cog.point(x, y, coord_crs=coord_projection, indexes=[1])
                co2_values.append(float(pointdata.data[0]))
            
            df["Fossil Fuel CO2 emissions"] = co2_values
        with Reader(s3_url_no2) as cog:    
            no2_values = []
            for _, row in df.iterrows():
                x, y = row["longitude"], row["latitude"]
                # Read pixel values for all bands at coordinates (x, y)
                pointdata = cog.point(x, y, coord_crs=coord_projection, indexes=[1])
                no2_values.append(float(pointdata.data[0]))
            
            df["Tropospheric Nitrogen Dioxide Emissions"] = no2_values
    else: 
        raise ValueError("Invalid version number. Must be 1.0.0 or 2.0.0")
    
    df["Rurality"] = df['rurality_id'].astype("str").map(rurality_def)
    df["Koppen Geiger"] = df["koppen_geiger_id"].astype("str").map(kg_def)
    
    return df

def main():
    parser = argparse.ArgumentParser(prog = "omeinfo.py", description = '''
                                     The OMEinfo command-line tool enables users to annotate geographical metadata, 
                                     including Koppen climate classification, degree of rurality, population density, 
                                     and fossil fuel CO2 emissions, from user-provided location data. 
                                     The tool offers options for selecting the data version and the data source. 
                                     Annotations are stored in a specified output file in TSV format.''')   

    parser.add_argument('--location_file', type = str, help = "file containing locations")
    parser.add_argument("--location", type = str, help = "location in latitude,longitude EPSG:4326 format, input string in format 'sample,latitude,longitude'")
    parser.add_argument("--data_version", type = str, help = "version of data to use", default = "2.0.0")
    parser.add_argument("--source_data", type = str, help = "url to data or filepath to local version")
    parser.add_argument("--output_file", type = str, help = "name of output file", default = "annotated_locations.tsv")
    parser.add_argument("--n_samples", type = int, help = "number of output summary table samples to show in command line", default = 10)
    parser.add_argument("--quiet", type = bool, help = "suppress console output", default = False)
    args = parser.parse_args()
    
    OMEINFO_CLI_VERSION = "1.0.0"
    OMEINFO_CONDA_PREFIX = os.environ.get('CONDA_PREFIX')
    console = Console()

    console.print(f"OMEinfo CLI Version: {OMEINFO_CLI_VERSION}", style = "bold green")
    if args.data_version == "1.0.0":
        bibtex_url = "https://raw.githubusercontent.com/m-crown/OMEinfo/main/citations/v1_citations.bib"
    elif args.data_version == "2.0.0":
        bibtex_url = "https://raw.githubusercontent.com/m-crown/OMEinfo/main/citations/v2_citations.bib"
    else:
        raise ValueError("Invalid version number. Must be 1.0.0 or 2.0.0")
    
    if args.source_data:
        console.print(f"Using user supplied source data: {args.source_data}, as data version {args.data_version}", style = "green")
    else:
        console.print(f"Using OMEinfo Data Version: {args.data_version}", style = "green")
    
    rurality_definitions = pd.read_csv(f"{OMEINFO_CONDA_PREFIX}/bin/rurality_legend.txt", sep = "\t")
    rurality_definitions["id"] = rurality_definitions["id"].astype("str")
    id_to_rurality = rurality_definitions.set_index('id')['definition'].to_dict()
    kg_definitions = pd.read_csv(f"{OMEINFO_CONDA_PREFIX}/bin/kg_legend.txt", sep = "\t")
    kg_definitions["id"] = kg_definitions["id"].astype("str")
    id_to_kg = kg_definitions.set_index('id')['definition'].to_dict()

    if args.location_file:
        if args.location_file.endswith('.csv'):
            delimiter = ','
        elif args.location_file.endswith('.tsv'):
            delimiter = '\t'
        else:
            raise ValueError("File format not supported. Please provide a CSV or TSV file.")
        locations_df = pd.read_csv(args.location_file, delimiter = delimiter)        #check sample latitude and longitude columns are present in dataframe
        
        if not set(["sample", "latitude", "longitude"]).issubset(set(locations_df.columns)):
            console.print("Location file must contain columns sample, latitude and longitude", style = "bold red")
            raise KeyError("Location file must contain columns sample, latitude and longitude")
    else:
        locations_df = pd.DataFrame()
    
    if args.location:
        individual_locations_df = pd.DataFrame([args.location.split(",")], columns = ["sample", "latitude", "longitude"])
        individual_locations_df[["latitude", "longitude"]] = individual_locations_df[["latitude", "longitude"]].astype(float)
        locations_df = pd.concat([locations_df, individual_locations_df])
    
    console.print(f"Loaded locations: {len(locations_df)}", style = "bold green")
    if len(locations_df) == 0:
        console.print("No locations provided. Exiting.", style = "bold red")
        raise ValueError("No locations provided. Exiting.")
    
    metadata_filtered_locations_df  = locations_df[locations_df[['sample', 'latitude', 'longitude']].notna().all(axis=1)]
    console.print(f"Missing required metadata: {len(locations_df) - len(metadata_filtered_locations_df)}", style = "bold red")  
    filtered_locations_df = metadata_filtered_locations_df[metadata_filtered_locations_df[['latitude', 'longitude']].apply(lambda x: -90 <= x["latitude"] <= 90 and -180 <= x["longitude"] <= 180, axis=1)]
    console.print(f"Invalid lat/long format: {len(metadata_filtered_locations_df) - len(filtered_locations_df)}", style = "bold red")      
    tasks = ["Annotating metadata"]

    with console.status("[bold green]Annotating metadata...") as status:
        while tasks:
            task = tasks.pop(0)
            start_time = datetime.datetime.now()
            annotated_locations = get_s3_point_data(filtered_locations_df.copy(), args.data_version, id_to_rurality, id_to_kg, user_url = args.source_data)
            end_time = datetime.datetime.now()
            c = end_time - start_time
            minutes = int(c.total_seconds() // 60)
            seconds = c.total_seconds() % 60
            console.print(f'Annotation complete! {str(len(filtered_locations_df))} samples analysed in {str(minutes)} mins {str(round(seconds,2))} secs. :white_check_mark:')
            annotated_locations.to_csv(args.output_file, index = False, sep = "\t")
            
            response = requests.get(bibtex_url)
            if response.status_code == 200:
                bibtex_content = response.text
                with open("omeinfo_citations.bib", "w") as file:
                    file.write(bibtex_content)
                console.print(f"BibTeX file downloaded successfully, saved to: omeinfo_citations.bib", style = "bold green")
            else:
                console.print(f"Failed to download BibTeX file. Status code: {response.status_code}")       

    
    if not args.quiet:
        if args.source_data:
            caption = f"OMEinfo annotation with user supplied data file: {args.source_data}"
        else:
            caption = f"OMEinfo annotation with OMEinfo Data Version: v{args.data_version}"
        annotated_locations.loc[annotated_locations["Tropospheric Nitrogen Dioxide Emissions"].isna() == False,"Tropospheric Nitrogen Dioxide Emissions"] = annotated_locations.loc[annotated_locations["Tropospheric Nitrogen Dioxide Emissions"].isna() == False,"Tropospheric Nitrogen Dioxide Emissions"].apply(lambda x: '{:.{}e}'.format(x, 2))
        annotated_locations[["Fossil Fuel CO2 emissions", "Population Density"]] = annotated_locations[["Fossil Fuel CO2 emissions", "Population Density"]].round(2)
        
        table = Table(show_header=True, header_style="bold magenta", title = f"OMEinfo metadata annotation summary (top {args.n_samples})", caption = caption, caption_justify = "center")
        for column in annotated_locations.columns:
            if column not in ["koppen_geiger_id", "rurality_id"]:
                table.add_column(str(column))
        row = []
        for index, value_list in enumerate(annotated_locations.drop(columns = ["koppen_geiger_id", "rurality_id"]).head(args.n_samples).values.tolist()):
            row = [str(x) for x in value_list]
            table.add_row(*row)
        console.print(table)


if __name__ == "__main__":
    main()

<p align="center">
  <img src="https://github.com/m-crown/OMEinfo/blob/9831a26e93ad7a9e3accec5c5e8d38ce83259c0c/OMEinfo/app/assets/logo.png" alt="OMEinfo Logo" width="40%" height="auto" />
</p>

OMEinfo is an open-source bioinformatics tool designed to automate the retrieval of consistent geographical metadata for microbiome research. It provides an easy-to-use interface for researchers to obtain geographical metadata, including Koppen climate classification, degree of rurality, population density, and fossil fuel CO2 emissions from user-provided location data. The tool aims to facilitate cross-study comparisons and promote reproducibility in microbiome research by adhering to the principles of FAIR and Open data.

## Features

- Dash web application for user-friendly data upload and visualization
- Custom Cloud Optimized GeoTIF file hosted on AWS S3 for efficient data access
- Integration with open data sources, such as Global Human Settlement Layer (GHSL)
- Portable and lightweight Docker container for easy deployment
- Adheres to FAIR and Open data principles for better reproducibility and collaboration

## Installation

OMEinfo is provided as a Docker container, which can be easily set up in a local environment or on cloud-based platforms. To install and run OMEinfo, follow these steps:

1. Install Docker on your machine following the [official installation guide](https://docs.docker.com/get-docker/).
2. Clone this repository: `git clone https://github.com/m-crown/OMEinfo.git`
3. Navigate to the project app directory: `cd OMEinfo/OMEinfo`
4. Build the Docker image: `docker build -t omeinfo .` Note: you may need to prefix this command with sudo.
5. Run the Docker container: `docker run -p 8050:8050 omeinfo`

## Usage

1. Open the OMEinfo web application in your browser at `http://0.0.0.0:8050`.
2. Upload a CSV file containing geolocation data (latitude and longitude) using the provided interface. A test addresses file is distributed with the OMEinfo repo , `OMEinfo/test_data`. `test_addresses` is a large sample metadata file, and can take some time to load. `test_addresses2.csv` is a subset of the larger set, and will load in approx 15 seconds. 
3. The application will retrieve the geographical metadata for the uploaded locations and display the results on a map and in a histogram.
4. You can choose to display metadata features as the color coding on the map and as the histogram's x-axis.
5. A table with the processed data is also provided for further analysis. 

## Data Sources

The cloud-optimized GeoTIFF files are stored on AWS S3 following a naming schema that includes the data type, source, and version number. The file names are constructed as follows:

`<data_type><source><version>.tif`

For example:

1. `CO2_v1.tif`
2. `rurpopkop_v1.tif`

When new data becomes available, the version number in the file name is incremented (e.g., `v2`, `v3`, etc.). This allows users to identify and access the most up-to-date version of the data while maintaining the availability of previous versions for reference or reproducibility purposes.

To ensure clear and consistent communication of version updates, a changelog will be maintained in this repository, documenting the dates of version updates and any significant changes in the data.

### Current Data Sources

| File Name     | File URL | Description |
|---------------|----------|-------------|
| co2_v1_cog.tif    | s3://cloudgeotiffbucket/co2_v1_cog.tif | Fossil Fuel CO2 Emissions |
| rurpopkop_v1_cog.tif | s3://cloudgeotiffbucket/rurpopkop_v1_cog.tif | Rurality, Population Density, and Koppen-Geiger Climate Classification |
| no2_v1_cog.tif | s3://cloudgeotiffbucket/no2_v1_cog.tif | Tropospheric NO2 Emissions |

For details on the process for creation of the current data sources, see explanation [here](https://m-crown.github.io/OMEinfo/data_processing.md)

### Citations

| Data Source | Citation | DOI |
|-------------|----------|-----|
| Fossil Fuel CO2 emissions data | Tomohiro Oda, Shamil Maksyutov (2015), ODIAC Fossil Fuel CO2 Emissions Dataset (Version name : ODIAC2020b), Center for Global Environmental Research, National Institute for Environmental Studies | [10.17595/20170411.001](https://doi.org/10.17595/20170411.001) |
| Koppen-Geiger Climate Classification | Beck, H., Zimmermann, N., McVicar, T. et al. Present and future Köppen-Geiger climate classification maps at 1-km resolution. Sci Data 5, 180214 (2018) | [10.1038/sdata.2018.214](https://doi.org/10.1038/sdata.2018.214) |
| Population Density | Schiavina, Marcello; Freire, Sergio; MacManus, Kytt (2019): GHS population grid multitemporal (1975, 1990, 2000, 2015) R2019A. European Commission, Joint Research Centre (JRC) | [10.2905/42E8BE89-54FF-464E-BE7B-BF9E64DA5218](https://doi.org/10.2905/42E8BE89-54FF-464E-BE7B-BF9E64DA5218) |
| Rurality | Pesaresi, Martino; Florczyk, Aneta; Schiavina, Marcello; Melchiorri, Michele; Maffenini, Luca (2019): GHS settlement grid, updated and refined REGIO model 2014 in application to GHS-BUILT R2018A and GHS-POP R2019A, multitemporal (1975-1990-2000-2015), R2019A. European Commission, Joint Research Centre (JRC) | [10.2905/42E8BE89-54FF-464E-BE7B-BF9E64DA5218](https://doi.org/10.2905/42E8BE89-54FF-464E-BE7B-BF9E64DA5218) |
| Tropospheric NO2 Emissions data | Romahn, Pedergnana, Loyola, Apituley, Sneep and Veefkind (2022): Sentinel-5 Precursor/TROPOMI Level 2 Product User Manual: Cloud Properties | [ESA Sentinel 5P](https://sentinel.esa.int/documents/247904/2474726/Sentinel-5P-Level-2-Product-User-Manual-Cloud) |

Download the [current citations in BibTeX format](citations/v1_citations.bib).

Past citations can be found in BibTeX format in the [citations](citations/) directory of OMEinfo.

## License

OMEinfo is released under the [MIT License](https://opensource.org/licenses/MIT). By using OMEinfo, you agree to the terms and conditions of this license. See the `LICENSE` file in this repo for more information.

## Support

If you encounter any issues or have questions regarding the use of OMEinfo, please create an issue on this repo.

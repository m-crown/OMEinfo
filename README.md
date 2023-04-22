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

## License

OMEinfo is released under the [MIT License](https://opensource.org/licenses/MIT). By using OMEinfo, you agree to the terms and conditions of this license. See the `LICENSE` file in this repo for more information.

## Support

If you encounter any issues or have questions regarding the use of OMEinfo, please create an issue on this repo.

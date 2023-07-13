#!/bin/sh
# This script merges multiple geotif files into a single output geotif using gdal. 
# Each geotif is merges as a single output layer in the output geotif. 
# Matt Crown 2023

# Check if the output filename and at least one input file were supplied as arguments
if [ -z "$1" ] || [ -z "$2" ]
then
    echo "Missing arguments. Please run the script with the output filename as the first argument and all input filenames as the remaining arguments."
    echo "You must include at least one input tif file."
    echo "Example: ./merge_tif.sh rurpopkop_v1.tif GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0.tif GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif Beck_KG_V1_present_0p0083_mollweide.tif"
    echo "Exiting..."
    exit 1
fi

# Store the output filename in a variable and shift the arguments
output_file=$1
shift

# Run the gdal_merge.py command with the specified output filename and input files
gdal_merge.py -separate -o $output_file "$@"
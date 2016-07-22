#!/bin/bash

# Purpose:
#       Script to add all nutrient files to database

data_dir="/Users/bell/ecoraid/2014/CTDcasts/ae1401/initial_archive/allparameters/"
data_files="/Users/bell/ecoraid/2014/CTDcasts/ae1401/final_data/ctd/*.nc"
prog_dir="/Users/bell/Programs/Python/AtSeaPrograms/PostCruiseRoutines/"

for files in $data_files
do
    echo "processing file: $files"
    newfile=$(basename $files)
    echo "adding to file: ${data_dir}${newfile}"
    python ${prog_dir}nc2nc_2files.py ${data_dir}${newfile} ${files} time
done


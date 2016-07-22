#!/bin/bash

# Purpose:
#       Script add a missing variable to selected cast files

data_dir="/Users/bell/ecoraid/2014/CTDcasts/ae1402/initial_archive/allparameters/"
data_files="/Users/bell/ecoraid/2014/CTDcasts/ae1402/final_data/ctd/*.nc"
prog_dir="/Users/bell/Programs/Python/AtSeaPrograms/utilities/"

for files in $data_files
do
    echo "processing file: $files"
    newfile=$(basename $files)
    echo "adding to file: ${data_dir}${newfile}"
    python ${prog_dir}nc2nc_2files.py ${data_dir}${newfile} ${files} time2
done
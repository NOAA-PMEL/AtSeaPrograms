#!/bin/bash

# Purpose:
#       Script to add all nutrient files to database


prog_dir="/Volumes/WDC_internal/Users/bell/Programs/Python/AtSeaPrograms/PostCruiseRoutines/"

data_dir_final="/Volumes/WDC_internal/Users/bell/ecoraid/2017/CTDcasts/dy1706l2/final_data/ctd/"
data_dir_source="/Volumes/WDC_internal/Users/bell/ecoraid/2017/CTDcasts/dy1706l2/initial_archive/*.nc"

for files in ${data_dir_source}
do
    names=(${files//\// })
    var=${names[${#names[@]} - 1]}
    outfile=${var%.*}

	echo "processing file: $files"
	python ${prog_dir}nc2nc_2files.py ${files} ${data_dir_final}${outfile}.nc CTDOXY_4221
done


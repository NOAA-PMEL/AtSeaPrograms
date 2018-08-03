#!/bin/bash

# Purpose:
#       Script to add all nutrient files to database


prog_dir="/Users/bell/Programs/Python/AtSeaPrograms/PostCruiseRoutines/"

data_dir_final="/Users/bell/ecoraid/2017/CTDcasts/nw1705/final_data/ctd/"
data_dir_source="/Users/bell/ecoraid/2017/CTDcasts/nw1705/initial_archive/*.nc"

for files in ${data_dir_source}
do
    names=(${files//\// })
    var=${names[${#names[@]} - 1]}
    outfile=${var%.*}

	echo "processing file: $files"
	python ${prog_dir}nc2nc_2files.py ${files} ${data_dir_final}${outfile}.nc Trb_980
done

for files in ${data_dir_source}
do
    names=(${files//\// })
    var=${names[${#names[@]} - 1]}
    outfile=${var%.*}

	echo "processing file: $files"
	python ${prog_dir}nc2nc_2files.py ${files} ${data_dir_final}${outfile}.nc PAR_905
done

#!/bin/bash

# Purpose:
#       Script to add all nutrient files to database


prog_dir="/Users/bell/Programs/Python/AtSeaPrograms/PostCruiseRoutines/"

data_dir="/Users/bell/ecoraid/2016/CTDcasts/cf1601/working/*.nc"

for files in $data_dir
do
	echo "processing file: $files"
	python ${prog_dir}4Ddepth_to_1Ddep.py ${files} 
done

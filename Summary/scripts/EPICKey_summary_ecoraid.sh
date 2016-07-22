#!/bin/bash

# Purpose:
#       Script to run CTDnc2odv.py for all .nc files in a directory

# older data streams -> 2011 or so
data_dir="/Users/bell/Data_Local/FOCI/CTD_orig/*/*/"
# ecoraid newer archive format
#data_dir="/Users/bell/ecoraid/*/CTDCasts/*/final_data/*/"
prog_dir="/Users/bell/Programs/Python/AtSeaPrograms/Summary/"

for files in $data_dir
do
    cruiseID=(${files//\// })
	#echo "processing file: ${cruiseID[${#cruiseID[@]}-1]}"
	python ${prog_dir}EPICkey_summary.py $files ${cruiseID[${#cruiseID[@]}-1]}
done

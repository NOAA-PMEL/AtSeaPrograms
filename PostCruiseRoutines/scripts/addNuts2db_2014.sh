#!/bin/bash

# Purpose:
#       Script to add all nutrient files to database


prog_dir="/Users/bell/Programs/Python/AtSeaPrograms/PostCruiseRoutines/"

path="/Users/bell/ecoraid/2014/CTDcasts/"


cruiseid='ae1401'

cruiseid='aq1401l2'
python ${prog_dir}Nut2DB.py ${path}${cruiseid}'/working/DiscreteNutrients/ArcWEST 2014 Nutrient Data edit.txt' ${cruiseid}

cruiseid='dy1405'
python ${prog_dir}Nut2DB.py ${path}${cruiseid}'/working/DiscreteNutrients/DY1405 Nutrient Data.txt' ${cruiseid}

cruiseid='dy1408l1'
python ${prog_dir}Nut2DB.py ${path}${cruiseid}'/working/DiscreteNutrients/DY1408 Nutrient Data.txt' ${cruiseid}

cruiseid='kh1401'
python ${prog_dir}Nut2DB.py ${path}${cruiseid}'/working/DiscreteNutrients/RS1401 Nutrient Data edit.txt' ${cruiseid}

#!/bin/bash

# Purpose:
#       Script to add all nutrient files to database


prog_dir="/Users/bell/Programs/Python/AtSeaPrograms/PostCruiseRoutines/"

path="/Users/bell/ecoraid/2015/CTDcasts/"

cruiseid='dy1508'
python ${prog_dir}Nut2DB.py ${path}${cruiseid}'/working/DiscreteNutrients/DY1508 Nutrient Data.txt' ${cruiseid}

cruiseid='dy1509'
python ${prog_dir}Nut2DB.py ${path}${cruiseid}'/working/DiscreteNutrients/DY1509 Nutrient Data.txt' ${cruiseid}

cruiseid='ae1501'
#not yet analyzed

cruiseid='aq1501'
python ${prog_dir}Nut2DB.py ${path}${cruiseid}'/working/DiscreteNutrients/AQ1501 Nutrient Data nisk_edit.txt' ${cruiseid}

cruiseid='dy1504'
python ${prog_dir}Nut2DB.py ${path}${cruiseid}'/working/DiscreteNutrients/DY1504 Nutrient Data.txt' ${cruiseid}

cruiseid='hly1501'
python ${prog_dir}Nut2DB.py ${path}${cruiseid}'/working/DiscreteNutrients/HE1501 Nutrient Data.txt' ${cruiseid}

cruiseid='nw1501'
#not yet analyzed
cruiseid='nw1502'
#not yet analyzed

cruiseid='rb1505'
python ${prog_dir}Nut2DB.py ${path}${cruiseid}'/working/DiscreteNutrients/RB1505 Nutrient Data.txt' ${cruiseid}

#!/bin/bash 


FOLDER="$1"
START=$2
END=$3
BLEND=lorenz_curve_blender_v09.blend


echo -e "Blend file name($BLEND)? "
read FILENAME

echo -e "Output folder ($FOLDER)? "
read DEST


echo -e "Start frame ($START)? "
#read IN


echo -e "End frame ($END)?"
#read OUT


blender -b "$BLEND" -o //render/$FOLDER/ -s $START -e $END -a


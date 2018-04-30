#!/bin/bash 


FOLDER="$1"
START=1
END=250
BLEND=lorenz_curve_blender_v09.blend

blender -b "$BLEND" -o //render/$FOLDER/ -s $START -e $END -a


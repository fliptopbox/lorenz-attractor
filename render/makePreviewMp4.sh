#!/bin/bash

# Makes a preview MP4 from a frame sequence
# the first argument determines the sequence folder name

# usage:
# sh makePreviewMp4.sh "exr"

EXT=$1

ffmpeg -y -i "./$EXT/%04d.$EXT" -c:v libx264 -vf fps=25,format=yuv420p "output_$EXT.mp4"
vlc "output_$EXT.mp4"

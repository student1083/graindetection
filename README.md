# Graindetection


# Overview

This command line script is designed to detect mineral fertilizer grains on a georeferenced image of a field.


# Installation Instructions

The script can be used either with the packaged graindetection.exe or the graindetection.py file.

## Packaged .exe file

In the graindetection.exe a bundled python distribution and both scripts are included, which means no additional
python distribution is needed to run the program on a Windows machine.

To run the command line program, download the .exe file and navigate with the command prompt to the location of the file.
From there the command line program can be used with `> graindetection.exe "path_to_file"`.

## Script .py Version

The script version contains two python scripts, where graindetection.py is the entry point script
and detection.py contains helper functions. The detection.py script must be in the same location as 
graindetection.py to work properly.
The requirements.txt file can be used to create an anaconda environment with all needed libraries installed.
To run the command line as a script, inside the conda environment run `> python graindetection.py "path_to_file"`.

# Functionality

The script implements a contour recognintion algortithm with global thresholding to detect fertilizer grains.
The preset parameters where optimally chosen for two sample images during development, therefore adapting those,
especially the threshold value, is important for good quality for users.

## Input

The input of the command line program is a georeferenced image in .tif file format.
The path for this file must be given as input for every run of the script.

## Output

The script outputs a .csv file with the coordinate values of all detected fertilizer grains.

## Other functionalities

The script offers viewing parts of the image which have been evaluated using `--visualize`.
The `--probe` command evaluates one part of the image with multiple threshold values and visualizes them to enable the
user to choose an according threshold value.

# Examples
A few examples of the functionality of the program.

## Visualize a random part of the image with the preset parameters

`> graindetection.exe "path_to_file" --visualize`

## Visualize a chosen part of the image with preset parameters
Visualizes the 300 by 300 pixel subimage with the top left corner being the pixel (120, 150).

`> graindetection.exe "path_to_file" --visualize -loc 120 150 300`

## Visualize a random part of the image with a different threshold value

`> graindetection.exe "path_to_file" --visualize -t 195`

## Probe the image for threshold values on a chosen part of the image
Shows a range of different threshold values evaluated on the 500 by 500 pixel subimage with top left corner (300,750).

`> graindetection.exe "path_to_file" --probe -loc 300 750 500`

## Detect all grains in the image and write coordinates into .csv file

Detects all grains in the whole image with the set threshold value 205 and slices the image into 3000 by 3000 subimages for the computation.
The output csv file is specified in "output_file_path".

`> graindetection.exe "path_to_file" -t 205 --slicingsize 3000 -o "output_file_path"`


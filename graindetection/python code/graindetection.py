# -*- coding: utf-8 -*-
"""
graindetection.py
"""

import detection
from rasterio.windows import Window
import argparse
import numpy as np
import random
import csv
import tqdm
import ast

# Initialize parser
parser = argparse.ArgumentParser()

# add argument for path to image always needed
parser.add_argument("file_path", type=str, help = "Path to georeferenced image in .tif format")

# Adding optional arguments
# add argument to visualize a chosen image location with a chosen threshold
parser.add_argument("--visualize", help = "Visualize a selected image with chosen parameters, if -loc is not specified a random location is chosen", action="store_true")

# add argument to probe the threshold
parser.add_argument("-p","--probe", help = "Shows a range of different values for the threshold evaluated on the image", action="store_true")

# add argument to choose destination of threshold probing
parser.add_argument("-loc","--location", nargs=3, help = "Sets left upper point and size of image for images with format '-loc x y size')")

# add argument to surpress output (for probing)
parser.add_argument("--surpress", "-s", action="store_true", help="Use to surpress output, does not create a result file if used")

# Version Argument
parser.add_argument("-v", "--version", help = "Print Version Number")

# add argument for threshold value
parser.add_argument("-t", "--threshold", help = "Value for thresholding between [0, 255], choose via --probe or leave empty for default value 208")

# add argument for blurring method
parser.add_argument("--blurmethod", type = str,  help = "Either 'average', 'gaussian', 'median', 'bilateral' or 'none' the default value is 'none'")

# add argument for blur format
parser.add_argument("--blurformat", type = str, help = "Blurring Parameters depending on blurmethod chosen, see documentation for more details")

# add argument for trim1
parser.add_argument("--trim1", type = int, choices = [0,1], help = "Set if you want to trim the result of outliers, default value is True")

# add argument for trim2
parser.add_argument("--trim2", type = int, choices = [0,1], help = "Set if you want to trim the result another time, default value is True")

# add argument for slicing size
parser.add_argument("--slicingsize", type = int, help = "Size of image slices which get loaded into memory at once, dependend on system memory and file size, default value is 2000")

# add argument to location of coordinate list
parser.add_argument("-o","--output", type = str, help = "Path to output file in csv format, default output file is created if not specified")

# Read arguments from command line
args = parser.parse_args()



# load image from filepath provided
if args.file_path.endswith(".tif"):
    src = detection.load_image(args.file_path)
else:
    print("File Format must be .tif")
    exit()

# set all values to default if not provided
if args.threshold:
    if args.threshold >= 0 and args.threshold <= 255:
        threshold = int(args.threshold)
    else:
        print("Threshold value must be in range [0, 255]")
        exit()
else:
    threshold = 208

if args.blurmethod:
    if args.blurmethod in ['none', 'average', 'gaussian', 'median', 'bilateral']:
        blurmethod = args.blurmethod
    else:
        print("Blurmethod must be either 'average', 'gaussian', 'median', 'bilateral' or 'none'")
        exit()
else:
    blurmethod = 'none'
    
if args.blurformat:
    blurformat = ast.literal_eval(args.blurformat)
else:
    blurformat = 'none'

if args.trim1 == 0:
    trim1 = False
else:
    trim1 = True
    
if args.trim2 == 0:
    trim2 = False
else:
    trim2 = True
    
if args.slicingsize:
    size = args.slicingsize
else:
    size = 2000
    
if args.output:
    if args.output.endswith(".csv"):
        outpath = args.output
    else:
        print("Filename must be of .csv format")
        exit()
else:
    outpath = "coordinate_list.csv"
    
# visualize image
if args.visualize:
    args.surpress = True
    if args.location:
        try:
            corner1 = int(args.location[0])
            corner2 = int(args.location[1])
            size = int(args.location[2])
            img = src.read(window=Window(corner1, corner2, size, size))
        except:
            print("The specified location using -loc produces an error, check if the upper left corner is within the image and size does not exceed the image parameters")
            exit()
    else:
        size = 1200
        corner1 = random.randint(0,src.width - size)
        corner2 = random.randint(0,src.height - size)
        img = src.read(window=Window(corner1, corner2, size, size)) 
    detection.draw_results(img, threshold, blurmethod, blurformat, trim1, trim2)

# probe image to visually decide for values
if args.probe:
    # during probing surpress output
    args.surpress = True
    if args.location:
        try:
            corner1 = int(args.location[0])
            corner2 = int(args.location[1])
            size = int(args.location[2])
            img = src.read(window=Window(corner1, corner2, size, size))
        except:
            print("The specified location using -loc produces an error, check if the upper left corner is within the image and size does not exceed the image parameters")
            exit()
    else:
        size = 500
        corner1 = random.randint(0,src.width - size)
        corner2 = random.randint(0,src.height - size)
        img = src.read(window=Window(corner1, corner2, size, size))
    detection.img_prober(img, blurmethod, blurformat, trim1, trim2)

# slice image
if not args.surpress:
    corners = detection.slice_image(src, size)
    
# run grain detection method on all slices, then compound into a list of coordinates
if not args.surpress:
    coordinate_list = []
    for corner_points in (pbar := tqdm.tqdm(corners)):
        pbar.set_description(f"Processing slice {corner_points}")
        # load relevant slice of the image into the program
        img = src.read(window=Window(corner_points[0], corner_points[1], min(size, src.width - corner_points[0]), min(size, src.height - corner_points[1])))
        # run pixel detection of the slice
        points_detected, additional, zero_moments = detection.contours_method(img, threshold, blurmethod, blurformat, trim1, trim2)
        if not type(points_detected) == int:
            # turn pixel values to coordinate values
            points_detected = points_detected + corner_points
            coordinates = src.transform * points_detected.T
            coordinates = np.concatenate((coordinates[0][np.newaxis].T, coordinates[1][np.newaxis].T), axis=1)
            # add coordinates to coordinate list
            for (i,j) in coordinates:
                coordinate_list.append((i,j))

# write coordinate list to specified output file
if not args.surpress:
    with open(outpath, 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['Longitude', 'Latitude'])
        for grain in coordinate_list:
            wr.writerow([grain[0], grain[1]])
            
print("The program has terminated.")
        
        
    


































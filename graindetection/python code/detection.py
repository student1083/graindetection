# -*- coding: utf-8 -*-
"""
image detection functionality
"""

import rasterio
from matplotlib import pyplot as plt
import numpy as np
import cv2
from matplotlib.patches import Circle
import matplotlib.patches as mpatches

# image loader
def load_image(path_to_image):
    try:
        src = rasterio.open(path_to_image)
        return src
    except:
        print("An error occured: File could not be read")
        
# slices large image in smaller chunks
def slice_image(src, size = 1500):
    width = src.width
    height = src.height
    x_vals = [i for i in range(0,width, size)]
    y_vals = [i for i in range(0,height, size)]
    corners = [[i, j] for i in x_vals for j in y_vals]
    return corners

# formats image to opencv format
def opencv_formatter(image):
    image = np.transpose(image[:3,:,:], (1,2,0))
    return image

# calculate zscore of 1-d numpy array
def zscore(array):
    if array.size > 1:
        mean_np = np.mean(array)
        std_dev_np = np.std(array)
        z_scores = (array - mean_np) / std_dev_np
        return z_scores
    else:
        return np.zeros(array.shape)

# detects grains and returns pixel values
def contours_method(image, thresh_var, blur, blurformat, trim, trim2):
    rgb_image = opencv_formatter(image)
    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    # blurring depending on choice
    if blur == 'average':
        gray_image = cv2.blur(gray_image, blurformat) # ex (5,5)
    elif blur == 'gaussian':
        gray_image = cv2.GaussianBlur(gray_image, blurformat[0], blurformat[1]) # ex [(3,3), 0]
    elif blur == 'median':
        gray_image = cv2.medianBlur(gray_image, blurformat) # ex 5
    elif blur == 'bilateral':
        gray_image = cv2.bilateralFilter(gray_image, blurformat[0], blurformat[1], blurformat[2]) # ex 9, 75, 75
    elif blur == 'none':
        gray_image = gray_image
    else:
        raise ValueError('blur only supports "average", "gaussian", "median", "bilateral" or "none" keywords.')
    # thresholding
    ret, thresh = cv2.threshold(gray_image, thresh_var, 255, cv2.THRESH_BINARY_INV)
    # finding contours
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    points_center = np.zeros((len(contours), 4))
    zero_moment_count = 0
    for i,c in enumerate(contours):
        # calculate moments
        M = cv2.moments(c)
        if M['m00'] != 0:
            cX = int(M['m10'] / M['m00'])
            cY = int(M['m01'] / M['m00'])
        else:
            cX, cY = 0, 0
            zero_moment_count = zero_moment_count + 1
        (x,y), radius = cv2.minEnclosingCircle(c)
        perimeter = cv2.arcLength(c, closed=True)
        points_center[i,:] = [cX, cY, radius, perimeter]
    # remove outlier with a large zscore twice, for huge outliers and trimming large objects
    if trim == True:
        z_score = zscore(points_center[:,2])
        delete_rows = np.where(np.abs(z_score) > 3)
        points_center = np.delete(points_center, delete_rows, 0)
    if trim2 == True:
        z_score = zscore(points_center[:,2])
        delete_rows = np.where(np.abs(z_score) > 2)
        points_center = np.delete(points_center, delete_rows, 0)
    # if only one grain was found discard it -> only use on larger images for more precise results
    if len(points_center[:, 0:2]) == 1:
        return 0,0,0
    return points_center[:, 0:2], points_center[:, 2:], zero_moment_count 

# calculate points and plot them on an image
def draw_results(img, threshold, blurmethod, blurformat, trim1, trim2):
    points_detected, additional, zero_moments = contours_method(img, threshold, blurmethod, blurformat, trim1, trim2)
    plt.ioff()  # maybe put in different place
    fig, ax = plt.subplots(1)
    img = opencv_formatter(img)
    ax.imshow(img)
    if type(points_detected) != int:
        for point in points_detected:
            circ = Circle(point.astype(int), 3, color='cyan', alpha=0.35)
            ax.add_patch(circ)
    detected = mpatches.Patch(color='cyan', alpha=0.35, label="Detected")
    ax.legend(handles=[detected])
    plt.show()

# draw four images in one figure with detected points highlighted
def draw_probe(img, points_detected_list, thresh_list):
    img = opencv_formatter(img)
    # turn off automatic displaying
    plt.ioff()
    # create empty 2 by 2 figure
    fig, ax = plt.subplots(2,2)
    # display first image with detected points
    ax[0,0].imshow(img)
    if type(points_detected_list[0]) != int:
        for point in points_detected_list[0]:
            circ = Circle(point.astype(int), 3, color='cyan', alpha=0.35)
            ax[0,0].add_patch(circ)
    detected = mpatches.Patch(color='cyan', alpha=0.35, label="Threshold =" + str(thresh_list[0]))
    ax[0,0].legend(handles=[detected])
    # display second image with detected points
    ax[1,0].imshow(img)
    if type(points_detected_list[1]) != int:
        for point in points_detected_list[1]:
            circ = Circle(point.astype(int), 3, color='cyan', alpha=0.35)
            ax[1,0].add_patch(circ)
    detected = mpatches.Patch(color='cyan', alpha=0.35, label="Threshold =" + str(thresh_list[1]))
    ax[1,0].legend(handles=[detected])
    # display third image with detected points
    ax[0,1].imshow(img)
    if type(points_detected_list[2]) != int:
        for point in points_detected_list[2]:
            circ = Circle(point.astype(int), 3, color='cyan', alpha=0.35)
            ax[0,1].add_patch(circ)
    detected = mpatches.Patch(color='cyan', alpha=0.35, label="Threshold =" + str(thresh_list[2]))
    ax[0,1].legend(handles=[detected])
    # display fourth image with detected points
    ax[1,1].imshow(img)
    if type(points_detected_list[3]) != int:
        for point in points_detected_list[3]:
            circ = Circle(point.astype(int), 3, color='cyan', alpha=0.35)
            ax[1,1].add_patch(circ)
    detected = mpatches.Patch(color='cyan', alpha=0.35, label="Threshold =" + str(thresh_list[3]))
    ax[1,1].legend(handles=[detected])
    return fig, ax

# probes image
def img_prober(img, blurmethod, blurformat, trim1, trim2):
    # detect points with different parameters and visualize
    threshold = np.arange(170, 230, 5)
    for i in range(3):
        thresh_list = []
        points_detected_list = []
        for j in range(4):
            thresh_list.append(threshold[i*4+j])
            points_detected, additional, zero_moments = contours_method(img, threshold[i*4+j], blurmethod, blurformat, trim1, trim2)
            points_detected_list.append(points_detected)
        fig, ax = draw_probe(img, points_detected_list, thresh_list)
        fig.tight_layout()
    plt.show()
    return
    





























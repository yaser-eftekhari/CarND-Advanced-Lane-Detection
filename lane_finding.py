import numpy as np
import pickle
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from line import Line

# Conversion between pixel and real distance (in meters)
ym_per_pix = 30/720 # meters per pixel in y dimension
xm_per_pix = 3.7/700 # meters per pixel in x dimension

# Detect the lines with no history
def detect_lines(image):
    # Take a histogram of the image
    histogram = np.sum(image, axis=0)

    # Find the peak of the left and right halves of the histogram
    # These will be the starting point for the left and right lines
    midpoint = np.int(histogram.shape[0]/2)
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    # calculate the lane distances from the center of the image
    # here we just use the base of the lane as a measure
    left_base_pos = (leftx_base - midpoint)*xm_per_pix
    right_base_pos = (rightx_base - midpoint)*xm_per_pix

    # Choose the number of sliding windows
    nwindows = 50
    # Set height of windows
    window_height = np.int(image.shape[0]/nwindows)
    # Identify the x and y positions of all nonzero pixels in the image
    nonzero = image.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    # Current positions to be updated for each window
    leftx_current = leftx_base
    rightx_current = rightx_base
    # Set the width of the windows +/- margin
    margin = 100
    # Set minimum number of pixels found to recenter window
    minpix = 50
    # Create empty lists to receive left and right lane pixel indices
    left_lane_inds = []
    right_lane_inds = []

    # Step through the windows one by one
    for window in range(nwindows):
        # Identify window boundaries in x and y (and right and left)
        win_y_low = image.shape[0] - (window+1)*window_height
        win_y_high = image.shape[0] - window*window_height
        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin

        # Identify the nonzero pixels in x and y within the window
        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
        # Append these indices to the lists
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)
        # If you found > minpix pixels, recenter next window on their mean position
        if len(good_left_inds) > minpix:
            leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

    # Concatenate the arrays of indices
    left_lane_inds = np.concatenate(left_lane_inds)
    right_lane_inds = np.concatenate(right_lane_inds)

    # Extract left and right line pixel positions
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]

    # Fit new polynomials to x,y in world space
    left_fit_cr = np.polyfit(lefty*ym_per_pix, leftx*xm_per_pix, 2)
    right_fit_cr = np.polyfit(righty*ym_per_pix, rightx*xm_per_pix, 2)
    # Calculate the new radii of curvature
    y_eval = image.shape[0]
    left_curverad = ((1 + (2*left_fit_cr[0]*y_eval*ym_per_pix + left_fit_cr[1])**2)**1.5) / np.absolute(2*left_fit_cr[0])
    right_curverad = ((1 + (2*right_fit_cr[0]*y_eval*ym_per_pix + right_fit_cr[1])**2)**1.5) / np.absolute(2*right_fit_cr[0])

    # Fit a second order polynomial to each
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)

    # Create two Line objects for the two lines and store the findings there
    left_line = Line(radius_of_curvature = left_curverad, line_base_pos = left_base_pos, current_fit = left_fit, all_points = (leftx, lefty))
    right_line = Line(radius_of_curvature = right_curverad, line_base_pos = right_base_pos, current_fit = right_fit, all_points = (rightx, righty))

    # Add the current fit to the list of previous fits
    left_line.add_fit(left_fit)
    right_line.add_fit(right_fit)

    return left_line, right_line

# Detect the lines based on previously found ones
def follow_lines(image, left_line, right_line):
    prev_left_fit = left_line.best_fit
    prev_right_fit = right_line.best_fit

    # Find nonzero elements in frame
    nonzero = image.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    margin = 100

    # Find benchmark lines to be used as the midpoint for line search
    leftx_current = prev_left_fit[0]*(nonzeroy**2) + prev_left_fit[1]*nonzeroy + prev_left_fit[2]
    rightx_current = prev_right_fit[0]*(nonzeroy**2) + prev_right_fit[1]*nonzeroy + prev_right_fit[2]
    # Window to find line pixels in
    win_xleft_low = leftx_current - margin
    win_xleft_high = leftx_current + margin
    win_xright_low = rightx_current - margin
    win_xright_high = rightx_current + margin
    # Identify the nonzero pixels in x and y within the window
    left_lane_inds = ((nonzerox > win_xleft_low) & (nonzerox < win_xleft_high))
    right_lane_inds = ((nonzerox > win_xright_low) & (nonzerox < win_xright_high))

    # Extract left and right line pixel positions
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]

    if leftx.size == 0 or rightx.size == 0:
        print("Switching to detect_lines")
        return detect_lines(image)

    # Fit a second order polynomial to each
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)

    # Generate x and y values for finding curvature
    ploty = np.linspace(0, image.shape[0]-1, image.shape[0])
    left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
    right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]

    # Fit new polynomials to x,y in world space
    left_fit_cr = np.polyfit(lefty*ym_per_pix, leftx*xm_per_pix, 2)
    right_fit_cr = np.polyfit(righty*ym_per_pix, rightx*xm_per_pix, 2)
    # Calculate the new radii of curvature
    y_eval = image.shape[0]
    left_curverad = ((1 + (2*left_fit_cr[0]*y_eval*ym_per_pix + left_fit_cr[1])**2)**1.5) / np.absolute(2*left_fit_cr[0])
    right_curverad = ((1 + (2*right_fit_cr[0]*y_eval*ym_per_pix + right_fit_cr[1])**2)**1.5) / np.absolute(2*right_fit_cr[0])

    # calculate the lane distances from the center of the image
    # here we just use the base of the lane as a measure
    midpoint = np.int(image.shape[1]/2)
    leftx_base = left_fit[0]*y_eval**2 + left_fit[1]*y_eval + left_fit[2]
    rightx_base = right_fit[0]*y_eval**2 + right_fit[1]*y_eval + right_fit[2]
    left_base_pos = (leftx_base - midpoint)*xm_per_pix
    right_base_pos = (rightx_base - midpoint)*xm_per_pix

    # Update Line objects from the newly found lines
    left_line.update(radius_of_curvature = left_curverad, line_base_pos = left_base_pos, current_fit = left_fit, all_points = (leftx, lefty))
    right_line.update(radius_of_curvature = right_curverad, line_base_pos = right_base_pos, current_fit = right_fit, all_points = (rightx, righty))

    left_line.add_fit(left_fit)
    right_line.add_fit(right_fit)

    return left_line, right_line

import numpy as np
import cv2
import glob
import matplotlib.pyplot as plt

chess_col_no = 10 - 1
chess_row_no = 7 - 1

# prepare object points, like (0,0,0), (1,0,0), (2,0,0), ..., (9,6,0)
objp = np.zeros((chess_row_no*chess_col_no,3), np.float32)
objp[:,:2] = np.mgrid[0:chess_col_no, 0:chess_row_no].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d points in real world space
imgpoints = [] # 2d points in image plane.

# Make a list of calibration images
images = glob.glob('camera_cal/calibration*.jpg')

# Step through the list and search for chessboard corners
for idx, fname in enumerate(images):
    # Read the calibration image
    img = cv2.imread(fname)
    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, (chess_col_no,chess_row_no), None)

    # If found, add object points, image points
    if ret == True:
        objpoints.append(objp)
        imgpoints.append(corners)

from random import randint
import pickle

# Test undistortion on an image
# Pick a random calibration image as test image
test_idx = randint(1, 20);
test_name = 'camera_cal/calibration'+str(test_idx)+'.jpg'
img = cv2.imread(test_name)
img_size = (img.shape[1], img.shape[0])

# Do camera calibration given object points and image points
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img_size, None, None)

# Undistort the test image and save the result
dst = cv2.undistort(img, mtx, dist, None, mtx)
test_output_name = 'camera_cal/calibrated'+str(test_idx)+'.jpg'
cv2.imwrite(test_output_name, dst)

# Save the camera calibration result for later use (we won't worry about rvecs / tvecs)
dist_pickle = {}
dist_pickle["mtx"] = mtx
dist_pickle["dist"] = dist
pickle.dump( dist_pickle, open( "camera_cal/calibration_pickle.p", "wb" ) )

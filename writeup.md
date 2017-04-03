#Advanced Lane Finding Project

This project is implemented in two phases:
1. Offline Phase: Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
2. Real-time Phase: Given a raw image, apply the following steps in sequence:
    1. Apply a distortion correction using calibration information from offline phase
    2. Use color transforms and thresholding to create a thresholded binary image
    3. Apply a perspective transform to rectify binary image ("birds-eye view")
    4. Detect lane pixels and fit to find the lane boundary
    5. Determine the curvature of the lane and vehicle position with respect to center
    6. Warp the detected lane boundaries back onto the original image
    7. Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position

[//]: # (Image References)

[Calibration]: ./output_images/calibration_output.png
[Undistortion]: ./output_images/undistorted_image.png
[Transformed]: ./output_images/perspective_transformation_output.png
[Binary]: ./output_images/binary_thresholding_output.png
[Output]: ./output_images/pipeline.png
[video]: ./final.mp4 "Video"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points

---
###Writeup / README

####Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Advanced-Lane-Lines/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

You're reading it!

---
###Camera Calibration

####Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

The code for this step can be found in `calibration.py`.  

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image.  Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  

I then used the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result: 

![Calibration Image Sample][Calibration]

Since camera calibration has to be done only once, at the end of this process, required parameters are saved in `camera_cal/calibration_pickle.p` pickle file. This file will be loaded when performing the pipeline on road images. This file has also been uploaded with the output images in `output_images` folder. 

---
###Pipeline (single images)

####1. Provide an example of a distortion-corrected image.
Loading the pickle file `calibration_pickle.p` discussed before and using `cv2.undistort()` any image can be undistored. Following is an example.
![Undistort a sample image][Undistortion]
####2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result. 
Best result was obtained in the Lab color space. The thresholding was relatively robust in different background colors and images with shaddows. The values for thresholds were found using trial and error.

This process can be found in `binary_threshold.py`. Here's an example of my output for this step. The green and blue indicate the thresholding result on L and B channels, respectively.

![Binary Transformation][Binary]

####3. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

The code for my perspective transform includes two functions `get_perspective()` and `warper()`, which appear in lines 50-51 and 42-47 in the file `perspective.py`, respectively. 

The `get_perspective()` is just a wrapper for the `warper()` function, which takes as inputs an image (`img`), as well as source (`src`) and destination (`dst`) points.  I chose the hardcode the source and destination points in the following manner, where `x_size` and `y_size` are the shape of the input image:

```
src_points = np.float32(
                        [[577, 460],
                        [705, 460],
                        [1040, 670],
                        [270, 670]])

dst_points = np.float32(
                        [[300, 0],
                        [x_size - 300, 0],
                        [x_size - 300, y_size],
                        [300, y_size]])

```
This resulted in the following source and destination points:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 577, 460      | 300, 0        | 
| 705, 460      | 980, 0        |
| 1040, 670     | 980, 720      |
| 270, 670      | 300, 720      |

I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image.

![Warping][Transformed]

####4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

The code for detecting the lane lines are in `lane_finding.py`. Lane detection is done using either functions `detect_lines()` or `follow_lines()`. Function `detect_lines()` is used when we are either in frame 0, or there is not enough information from previous frames to track the lines. On the contrary, function `follow_lines()` depends on the previously found lines and fitted polynomials to find the lines in the current frame. Both these functions operate on images in the perspective domain.

Function `detect_lines()` follows the following steps:
* Find the historgram of the frame
* Find two peaks of histogram on both sides of the midpoint of the image
* Starting from the peaks as base of each line, find pixels within a certain range
* Concatenate all found pixels and fit it with a second order polynomial (lines 89 and 90)
* Find the relative position of the car as well as the line curvature
* Create Line objects for the left and right lines

Function `follow_lines()` follows the following steps:
* Find pixels within a margin from the best fit calculated from previous iterations
* In case there is an issue finding the line pixels switch to `detect_lines()`
* Fit a polynomial to the found line pixels and find the relative position of the car as well as the line curvature
* Update left and right Line objects

####5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

In order to find the curvature, found left and right line pixels are scaled w.r.t. real world metrics. Then fitted second order polynomials are calculated using `numpy.polyfit` on the scaled points and fed into the formula presented in the course. For the two functions discussed above these steps can be found in lines 80-86 and 139-150 `lane_finding.py`.

####6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

I implemented this step in lines 75 through 79 in `run.py`.  Here is an example of my result on a test image:

![Pipeline Output][Output]

The pipeline itself can be seen in `run.py` file. Lines 55-72 will produce the video output and lines 75-79 produce the image output. Depending on the need, appropriate lines have to be commented out.

---

###Pipeline (video)

####Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a [link to my video result](./output_images/final.mp4)

---

###Discussion

####Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

**Perspective Mapping**

In choosing the source points I made sure the left and right ones were mirror with respect to the vertical center of the image. This ensures the center of frame is mapped to the center of the car.

**Line Class**

A Line class (`Line.py`) has been used to keep useful information about each line.

**Averaging Line Stats**

In each iteration fitted polynomials are added to a list and averaged to calculated the best fit. This estimate will be used to generate search boundaries for finding line pixels and drawing regions between the left and right lines in the visualization step.

**Left and Right Line Estimation**

I noted that left and right curvature should be the same as these lines are parallel to each other in perspective domain. This means that the fitted polynomials for left and right lines should only differ in their third element (offset). I tried to come up with a metic to decide between a well and poorly detected line. In this case the poorly detected line could have been estimated using the fitted polynomial of the other lane with some change into its offset parameter. This took sometime and ultimately I could not find such a metric. However, in theory this should work :D

**Color Space and Binary Thresholding**

I experimented with various color spaces and gradient thresholds to generate a binary image:
1. Using HLS color space; use L like grayscale and S to detect lines.
2. Using RGB color space; use R to detect lines.
3. Using HLS and RGB together. 
    * Adding R and S channels and applying threshold on the addition yields relatively good results and allows for separating lines from bright-colored ashphalt.
4. Using Lab color space; using the L and B channels

Many experiments and dstacks were generated and finally the sole use of Lab color space achieved the desired result.

This color space has not been used on other challenging videos. There is a high chance that thresholds found for the project video are not good for the challenging videos. In those cases a mix of all color spaces and possibly adaptive thresholding should be used.

I also experimented using thresholding in perspective domain. However, due to low resolution of farther lines it did not yield a good result.

I also experimented using Gaussian blurring to reduce the noise on the section between the two lines when using HLS and RGB color spaces. But that also did not achieve good results.

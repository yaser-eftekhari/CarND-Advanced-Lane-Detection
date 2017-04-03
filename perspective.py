import pickle
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

# Overlay lines and the region between them on the original image
def generate_final_image(image, left_line, right_line):
    color_warp = np.zeros_like(image).astype(np.uint8)

    y_limit = image.shape[0]
    x_limit = image.shape[1]
    left_fit = left_line.best_fit
    right_fit = right_line.best_fit

    ploty = np.linspace(0, y_limit-1, y_limit)
    left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
    right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]

    # Recast the x and y points into usable format for cv2.fillPoly()
    pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
    pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
    pts = np.hstack((pts_left, pts_right))

    # Draw the lane onto the warped blank image
    cv2.fillPoly(color_warp, np.int_([pts]), (0,255, 0))

    # Draw the left and right lanes in red and blue, respectively
    leftx, lefty = left_line.all_points
    rightx, righty = right_line.all_points
    color_warp[lefty, leftx] = [255, 0, 0]
    color_warp[righty, rightx] = [0, 0, 255]

    # Warp the lines back to camera space using inverse perspective matrix (Minv)
    newwarp = warper(color_warp, dst_points, src_points)
    # Combine the result with the original image
    result = cv2.addWeighted(image, .8, newwarp, .5, 0)

    return result

# Compute and apply perpective transform
def warper(img, src, dst):
    img_size = (img.shape[1], img.shape[0])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, img_size, flags=cv2.INTER_NEAREST)  # keep same size as input image

    return warped

# Transform the image from camera space to perspective
def get_perspective(img):
    return warper(img, src_points, dst_points)

# Source and destination points used for perspective mapping
src_points = np.float32(
                        [[577,460],
                        [705,460],
                        [1040,670],
                        [270,670]])

x_margin = 300
y_margin = 0
x_size = 1280
y_size = 720
dst_points = np.float32(
                        [[x_margin,y_margin],
                        [x_size - x_margin,y_margin],
                        [x_size - x_margin,y_size - y_margin],
                        [x_margin,y_size - y_margin]])

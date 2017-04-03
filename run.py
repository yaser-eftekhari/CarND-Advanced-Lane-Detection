# Import required libraries
import numpy as np
import pickle
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Import required functions from local files
from binary_threshold import bin_threshold
from perspective import get_perspective, generate_final_image
from lane_finding import detect_lines, follow_lines
from line import Line

# The pipeline to process an image, detect lines, draw region between lines and output the overlayed images
def e2e_pipeline(img):
    global processed_frames
    global left_line, right_line

    # Undistort the image
    image = cv2.undistort(img, mtx, dist, None, mtx)
    # Threshold the undistorted image and detect the lines
    combined_binary = bin_threshold(image)
    # Transform the image into the perspective domain
    warped = get_perspective(combined_binary)

    # Process the image differently depending on the first time or not
    if processed_frames == 0:
        left_line, right_line = detect_lines(warped)
    else:
        left_line, right_line = follow_lines(warped, left_line, right_line)

    processed_frames += 1

    # Find the curvature and relative position of the car
    avr_curverad = (left_line.radius_of_curvature + right_line.radius_of_curvature)/2
    left_base_pos = left_line.line_base_pos
    right_base_pos = right_line.line_base_pos
    base_pos = (left_base_pos + right_base_pos)/2

    # Generate the final image by overlaying lines and regions on the image
    ultimate = generate_final_image(image = image, left_line = left_line, right_line = right_line)

    # Print stats information on the image
    curv_text = 'Curvature: ' + str(int(avr_curverad)) + ' m'
    if base_pos > 0:
        pos_text = 'Car Offset: ' + str("%.2f" % base_pos) + ' m to the right'
    else:
        pos_text = 'Car Offset: ' + str("%.2f" % (-1*base_pos)) + ' m to the left'

    cv2.putText(ultimate, curv_text, (400, 100), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = 3, color = (255,255,255), thickness = 3)
    cv2.putText(ultimate, pos_text, (250, 150), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = 3, color = (255,255,255), thickness = 3)

    return ultimate

# Load the calibrarion information
calibration_pickle = pickle.load( open( "camera_cal/calibration_pickle.p", "rb" ) )
mtx = calibration_pickle["mtx"]
dist = calibration_pickle["dist"]

# Process the movie file, frame by frame
processed_frames = 0
left_line = None
right_line = None
from moviepy.editor import VideoFileClip

output = 'output_project_video.mp4'
frames = VideoFileClip("project_video.mp4")

single_frame = frames.fl_image(e2e_pipeline)
single_frame.write_videofile(output, audio=False)

print("processed_frames:", processed_frames)


# test_name = 'test_images/test3.jpg'
# img = mpimg.imread(test_name)
# ultimate = e2e_pipeline(img)
# plt.imshow(ultimate)
# plt.show()

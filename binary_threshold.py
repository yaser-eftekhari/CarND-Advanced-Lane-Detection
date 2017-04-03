import numpy as np
import pickle
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def bin_threshold(img, l_thresh=(210, 255), b_thresh=(160, 255)):
    img = np.copy(img)
    # Convert to LAB color space and separate the L and B channels
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2Lab)
    l_channel = lab[:,:,0]
    b_channel = lab[:,:,2]

    # Threshold on L and B channels and combine the results
    l_binary = np.zeros_like(l_channel)
    b_binary = np.zeros_like(b_channel)
    combined_binary = np.zeros_like(b_channel)

    l_binary[(l_channel >= l_thresh[0]) & (l_channel <= l_thresh[1])] = 1
    b_binary[(b_channel >= b_thresh[0]) & (b_channel <= b_thresh[1])] = 1
    combined_binary[(l_binary == 1) | (b_binary == 1)] = 1

    return combined_binary

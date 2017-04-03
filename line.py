import numpy as np

# Define a class to receive the characteristics of each line detection
class Line():
    #number of samples to average
    total_samples = 10
    def __init__(self, radius_of_curvature = None, line_base_pos = None, current_fit = [np.array([False])], all_points = None):
        #polynomial coefficients averaged over the last total_samples iterations
        self.best_fit = None
        #polynomial coefficients for the most recent fit
        self.current_fit = current_fit
        #radius of curvature of the line in some units
        self.radius_of_curvature = radius_of_curvature
        #distance in meters of vehicle center from the line
        self.line_base_pos = line_base_pos
        #x,y values for detected line pixels
        self.all_points = all_points
        #keeps the last few "good" line coefficients
        self.last_few_fit_coeffs = np.zeros((self.total_samples, 3))
        #keeps track of the next available cell in last_few_fit_coeffs
        self.next_available_index = 0
        #keep track of number of fits added for averaging purposes
        self.no_fits = 0

    def add_fit(self, fit):
        self.last_few_fit_coeffs[self.next_available_index, :] = fit
        self.next_available_index = (self.next_available_index + 1) % self.total_samples
        self.no_fits = min(self.no_fits + 1, self.total_samples - 1)
        self.best_fit = np.mean(self.last_few_fit_coeffs[:self.no_fits,:], axis = 0)

    def update(self, radius_of_curvature = None, line_base_pos = None, current_fit = [np.array([False])], all_points = None):
        #polynomial coefficients for the most recent fit
        self.current_fit = current_fit
        #radius of curvature of the line in some units
        self.radius_of_curvature = radius_of_curvature
        #distance in meters of vehicle center from the line
        self.line_base_pos = line_base_pos
        #x,y values for detected line pixels
        self.all_points = all_points

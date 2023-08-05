#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 18:18:04 2014
@author: Joel

Description:

"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon


def done(self):
    self.lineEdit_min_roundness.setText(str(self.clustering_window.lineEdit_min_roundness.text()))
    self.lineEdit_max_roundness.setText(str(self.clustering_window.lineEdit_max_roundness.text()))
    self.lineEdit_min_size.setText(str(self.clustering_window.lineEdit_min_size.text()))
    self.lineEdit_max_size.setText(str(self.clustering_window.lineEdit_max_size.text()))
    self.lineEdit_epsilon.setText(str(self.clustering_window.doubleSpinBox_distance.value()))
    self.lineEdit_min_pts.setText(str(self.clustering_window.doubleSpinBox_min_points.value()))
    self.spinBox_resolution.setValue(self.clustering_window.spinBox_resolution.value())
    self.lineEdit_min_density.setText(str(self.clustering_window.lineEdit_min_density.text()))
    self.lineEdit_max_density.setText(str(self.clustering_window.lineEdit_max_density.text()))
    self.clustering_window.close()


def plot_colonies_clustering(self):
    # Read in values from the gui
    self.min_roundness = float(self.clustering_window.lineEdit_min_roundness.text())
    self.max_roundness = float(self.clustering_window.lineEdit_max_roundness.text())
    self.min_size = float(self.clustering_window.lineEdit_min_size.text())
    self.max_size = float(self.clustering_window.lineEdit_max_size.text())
    self.min_density = float(self.clustering_window.lineEdit_min_density.text())
    self.max_density = float(self.clustering_window.lineEdit_max_density.text())
    self.ch1_min = float(self.clustering_window.lineEdit_ch1_min.text())
    self.ch1_max = float(self.clustering_window.lineEdit_ch1_max.text())
    self.ch2_min = float(self.clustering_window.lineEdit_ch2_min.text())
    self.ch2_max = float(self.clustering_window.lineEdit_ch2_max.text())
    self.ch3_min = float(self.clustering_window.lineEdit_ch3_min.text())
    self.ch3_max = float(self.clustering_window.lineEdit_ch3_max.text())
    self.top_edge = self.clustering_window.doubleSpinBox_top_edge.value() / 100
    self.bottom_edge = self.clustering_window.doubleSpinBox_bottom_edge.value() / 100
    self.left_edge = self.clustering_window.doubleSpinBox_left_edge.value() / 100
    self.right_edge = self.clustering_window.doubleSpinBox_right_edge.value() / 100

    data = self.clustering_window.data_cluster[
        self.clustering_window.data_cluster.Well==self.clustering_window.comboBox_wells.currentText()]#[random.random() for i in range(10)]
    color = data[str(self.clustering_window.comboBox_color.currentText())].values
#    color = data.AvgIntenCh2.values  
#        if MainWindow.checkBox_low_resolution.isChecked():
#            self.pixsize = 256
#        else:
#    data = data.loc[data.Top <= data.Top.quantile(1 - self.top_edge)]
#    data = data.loc[data.Top >= data.Top.quantile(self.bottom_edge)]
#    data = data.loc[data.Left >= data.Left.quantile(self.left_edge)]
#    data = data.loc[data.Left <= data.Left.quantile(1 - self.right_edge)]
    #Filter out based on position
    #Filter out cells based on intensities (Ishould just create a temp data variable in the future so that
    # I ca nload the data only once and then modify the plotted data instead of the real data)
    if 'ObjectAvgIntenCh1' in data.columns:
        data = data.loc[(data.ObjectAvgIntenCh1 <= self.ch1_max) &
            (data.ObjectAvgIntenCh1 >= self.ch1_min)]
    if 'AvgIntenCh2' in data.columns:
        data = data.loc[(data.AvgIntenCh2 <= self.ch2_max) &
            (data.AvgIntenCh2 >= self.ch2_min)]
    if 'AvgIntenCh3' in data.columns:
        data = data.loc[(data.AvgIntenCh3 <= self.ch3_max) &
            (data.AvgIntenCh3 >= self.ch3_min)]
    #Grab the value from the spinbox, which calculated automatically when the
    #clustering window loads, but can also be changed afterwards by the user
    #self.pixsize = self.clustering_window.spinBox_resolution.value()
    #TODO Fix this, need to grab from main UI ? Or just leave like this
    if np.any([self.data.Top.max() <= 256, self.data.Left.max() <= 256]):
        self.spinBox_resolution.setValue(256)
        self.pixsize = 256
    elif np.any([self.data.Top.max() <= 512, self.data.Left.max() <= 512]):
        self.spinBox_resolution.setValue(512)
        self.pixsize = 512
    elif np.any([self.data.Top.max() <= 1024, self.data.Left.max() <= 1024]):
        self.spinBox_resolution.setValue(1024)
        self.pixsize = 1024
    elif np.any([self.data.Top.max() <= 2048, self.data.Left.max() <= 2048]):
        self.spinBox_resolution.setValue(2048)
        self.pixsize = 2048
 #   self.pixsize = 512
#     print(self.pixsize)
#    self.pixsize = 512
    #Preallocate new series in the data frame
    data['LeftPixsize'] = np.nan
    data['TopPixsize'] = np.nan
    self.fieldlookuptable = np.array([ #FIXME and check nafees data and flip updown
        [91, 92, 93, 94, 95, 96, 97, 98, 99, 100],
        [90, 57, 58, 59, 60, 61, 62, 63, 64, 65],
        [89, 56, 31, 32, 33, 34, 35, 36, 37, 66],
        [88, 55, 30, 13, 14, 15, 16, 17, 38, 67],
        [87, 54, 29, 12,  3,  4,  5, 18, 39, 68],
        [86, 53, 28, 11,  2,  1,  6, 19, 40, 69],
        [85, 52, 27, 10,  9,  8,  7, 20, 41, 70],
        [84, 51, 26, 25, 24, 23, 22, 21, 42, 71],
        [83, 50, 49, 48, 47, 46, 45, 44, 43, 72],
        [82, 81, 80, 79, 78, 77, 76, 75, 74, 73],])
    #The given x and y coordinates from the cellomics instrument are relative to
    #each field. The below transforms the coordinates to be relative to each well
    #depending on which scanning pattern the user chose
    x_coordinates = np.zeros(len(data))
    y_coordinates = np.zeros(len(data))
    for field_num, field in enumerate(data.Field):
        x_coordinates[field_num] = np.where(self.fieldlookuptable == field)[0]
        y_coordinates[field_num] = np.where(self.fieldlookuptable == field)[1]
    data.TopPixsize = data.Top + self.pixsize * x_coordinates
    data.LeftPixsize = data.Left + self.pixsize * y_coordinates
    #Filter based on position
    data = data.loc[data.TopPixsize <= data.TopPixsize.max() * (1 - self.top_edge)]
    data = data.loc[data.TopPixsize >= data.TopPixsize.min() + (data.TopPixsize.max() * self.bottom_edge)]
    data = data.loc[data.LeftPixsize <= data.LeftPixsize.max() * (1 - self.right_edge)]
    data = data.loc[data.LeftPixsize >= data.LeftPixsize.min() + (data.LeftPixsize.max() * self.left_edge)]
    current_cells = np.array((data.LeftPixsize.values, data.TopPixsize.values)).T
    db = DBSCAN(eps=self.clustering_window.doubleSpinBox_distance.value(),
        min_samples=self.clustering_window.doubleSpinBox_min_points.value()).fit(current_cells)
    ax = self.clustering_window.widget_matplotlib.canvas.ax
    # discards the old graph
    ax.clear()
    # Keep X and Y lims the same
    ax.set(aspect='equal')
    # plot data
#    ax.scatter(data.LeftPixsize, data.TopPixsize, s = 15, c = [0.15,1,.15], cmap = plt.cm.hot,
#        marker = '.', linewidths=0.05, alpha = 0.9)
    ax.scatter(data.LeftPixsize, data.TopPixsize,
    s = 18, c = color, cmap = plt.cm.gist_heat, marker = '.', edgecolor='none', linewidths=0.1)
#    vmin = self.colorbar_min_array[self.file_num, 0], #The min of the colorscale
#    vmax = self.colorbar_max_array[self.file_num, 0], #The max of the colorscale
#    edgecolor = edgecolor, alpha = 0.6)
#    pprint('labbefore ')
#    pprint(db.labels_)
    colony_size_dict = []
    for colony_label in np.unique(db.labels_):
        #Relabel too small and too big colonies as noise
#        pprint([self.min_size, len(data[db.labels_ == colony_label].index), self.max_size])
#        pprint([type(self.min_size), type(len(data[db.labels_ == colony_label].index)), type(self.max_size)])
#        print(self.min_size > len(data[db.labels_ == colony_label].index) > self.max_size)
        colony_size = len(data[db.labels_ == colony_label].index)
        if not self.min_size < colony_size < self.max_size: #TODO maybe just ignore these colonies instead of relabeling
            db.labels_[db.labels_ == colony_label] = -1
        else:
            #Append only the size of non-noise colonies to the dict
            colony_size_dict.append(colony_size)
                #Calculate the roundness of the colony (this is done at three places in the code,
        #TODO calculate at only one place when I have the time to reanrange this...)
#        else:
#            idx_colony = self.idx_cells_well[self.labels == colony_label]
#            #Group cells after colonies so that they can be used to calculate the convex hull in -plot_colonies-
#            cells_in_colonies = np.asarray([self.data.LeftPixsize.iloc[idx_colony].values,
#                self.data.TopPixsize.iloc[idx_colony].values]).T
#            hull = ConvexHull(cells_in_colonies)
#            pol = Polygon(cells_in_colonies[hull.vertices])
#            colony_area = pol.area
#            colony_roundness = colony_area/pol.length**2 * 4 * np.pi
#            if not self.min_roundness < colony_roundness < self.max_roundness:
#                self.labels[self.labels == colony_label] = -1
#            else:
#                if not self.min_density < (colony_size / (1000000 * colony_area)) < self.max_density:
#                    self.labels[self.labels == colony_label] = -1
#            pprint('labafterequals')
#            pprint(db.labels_[db.labels_ == colony_label])
#    pprint('\nlabafter')
#    pprint(db.labels_)
    cells_in_colonies2 = []
    for colony_label in np.unique(db.labels_):
        if colony_label != -1:

            #Create a new index for each colony except the noise
            idx_colony = np.where(db.labels_ == colony_label)
            #Group cells after colonies so that they can be used to calculate the convex hull in -plot_colonies_clustering-
            cells_in_colonies2.append(np.asarray([data.LeftPixsize.iloc[idx_colony].values,
                data.TopPixsize.iloc[idx_colony].values]).T)
    #Draw convex hull
    roundness_dict = []
    density_dict = []
    for hull_points_idx, hull_points_array in enumerate(cells_in_colonies2):
        #ConvexHull and Delauny needs at least three values, errors otherwise, maybe try/except instead?
        #Also, all cells cannot be of the same x or y coordinate. The convex hull
        #can only be drawn if there are 2 dimensions
        if len(hull_points_array) > 2 and np.all([
           min(hull_points_array[:,0]) != max(hull_points_array[:,0]),
           min(hull_points_array[:,1]) != max(hull_points_array[:,1])]):
            hull = ConvexHull(hull_points_array)
            #Use the hull vertices to check how circular the object is. Only 
            #include the colony if it is within the given roundness range
            #This calculation is a measrue of compactness (in this case roundness)
            #http://gis.stackexchange.com/questions/85812/easily-calculate-roundness-compactness-of-a-polygon
            #There are many other ways to do this, but this is good for now
            #It does not identify objects that are not equivilateral very well but for 
            #equilateral object the below boundaries are accurate
#            pol_triangle = 0.5999908074321633
#            pol_square = 0.7853981633974483
#            pol_circle = 1
            pol = Polygon(hull_points_array[hull.vertices])
            colony_area = pol.area
#            print(colony_size * 10**6 / colony_area)
            colony_roundness = (colony_area / pol.length**2) * 4 * np.pi
            colony_density = colony_size * 10**6 / colony_area
            roundness_dict.append(colony_roundness)
            density_dict.append(colony_density)
            if self.min_roundness < colony_roundness < self.max_roundness:
                if self.min_density < colony_density < self.max_density:
                    for simplex in hull.simplices: #Hull simplices are the indices for -cells_in_colonier- of the cells incuded in the convex hull
                        # ax.hold(True)
                        ax.plot(hull_points_array[simplex,0],
                                 hull_points_array[simplex,1],
                                 'springgreen',
                                 linestyle = '-',
                                 linewidth=2)
    # refresh canvas
    ch2_mean = 0
    ch3_mean = 0
    ch4_mean = 0
    if 'AvgIntenCh2' in data.columns:
        try:
            ch2_mean = int(data.loc[db.labels_ != -1].AvgIntenCh2.mean())
        except ValueError: #sometime the above is NaN since there is only noise in the well
            ch2_mean = 0
    if 'AvgIntenCh3' in data.columns:
        try:
            ch3_mean = int(data.loc[db.labels_ != -1].AvgIntenCh3.mean())
        except ValueError:
            ch3_mean = 0
    if 'AvgIntenCh4' in data.columns:
        try:
            ch4_mean = int(data.loc[db.labels_ != -1].AvgIntenCh4.mean())
        except ValueError:
            ch4_mean = 0
    if len(db.labels_[db.labels_ != -1]) > 0:
        str_avgs = ('Mean roundness\t ' + str(round(np.mean(np.array(roundness_dict)),3)) +
            '\nMean density\t ' + str(int(np.mean(np.array(density_dict)))) +
            '\nMean size\t\t ' + str(int(np.mean(np.array(colony_size_dict)))) +
            '\nCh2 mean\t\t ' + str(ch2_mean) + '\nCh3 mean\t\t ' + str(ch3_mean) +
            '\nCh4 mean\t\t ' + str(ch4_mean))
        self.clustering_window.textEdit_avgs.setText(str_avgs)
        # Plot the a 500 units long scale bar
        ylim_mean = np.mean(ax.get_ylim())
        xlim_mean = np.mean(ax.get_xlim())
        ypos = ax.get_ylim()[0] + ylim_mean*0.03
        ax.plot([xlim_mean-250, xlim_mean+250], [ypos, ypos], linewidth=1.5,
            color='k')
        ax.scatter([xlim_mean-250, xlim_mean+250], [ypos, ypos], marker="|",
            s=40, linewidths=(1.5, 1.5), color='k')
        ax.annotate('500 units', xy=(xlim_mean, ypos), xytext=(0, -10),
            ha='center', textcoords='offset points', fontsize=9)

    self.clustering_window.widget_matplotlib.canvas.draw()

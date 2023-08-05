#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 16:50:41 2013
@author: Joel

Includes all the plotting functions and decorations for different colorscales
and thresholds.
"""

import matplotlib.pyplot as plt
from datetime import datetime
from time import time
import numpy as np

def plot_wells_solocpu(self):
    self.tp('Plotting...')
    self.tp('Well\tCells\tTime(s)')
    start_time = time()
#        self.pushButton_identify_colonies.setEnabled(False)
    my_dpi = 96
    fig_plot_wells = plt.figure(figsize=(1920/my_dpi, 1080/my_dpi), dpi=my_dpi)
    fig_plot_wells.suptitle(os.path.basename(self.file_path),
        fontsize=6, fontstyle='normal', color='grey')
    # Find extreme values so that all plots can have the same axis limits
    # Todo could set sharex and sharey to true instead, but can I use margins?, actually not that easy to use sharex since I am not calling plt.subplots with al plots at once
    xmin = self.data['LeftPixsize'].min() * 0.95
    xmax = self.data['LeftPixsize'].max() * 1.05
    ymin = self.data['TopPixsize'].min() * 0.95
    ymax = self.data['TopPixsize'].max() * 1.05
    color_col = self.comboBox_well_plot_color.currentText()

    if self.data[color_col].dtype in [float, int]:
        color_param = self.data[color_col]
    else: # For boolean and strings (objects)
        # TODO fix so that the default number of colors ~4-6 looks prettier
        unique_items = self.data[color_col].unique()
        num_colors = unique_items.shape[0]
        colors = plt.cm.Set1(np.linspace(0, 255, num=num_colors, dtype=int))
        items_colors = {x: y for x, y in zip(unique_items, colors)}
        color_param = self.data[color_col].apply(lambda x: items_colors[x])

    for well_name, well_df in self.data.groupby('Well'):
        start_time_well = time()
        # Returning the figure is actually redundant, but it looks cleaner
        fig_plot_wells = plot_wells(self.well_labels, well_name, well_df,
            fig_plot_wells, xmin, xmax, ymin, ymax, self.well_colony_vertices,
            color_param.loc[well_df.index])
        end_time_well = round(time() - start_time_well, 2)
        self.tp('{}\t{}\t{}'.format(well_name, well_df.shape[0], end_time_well))
    fig_plot_wells.tight_layout(rect=[0.05,0,0.95,0.97])

    end_time_plot = round(time() - start_time, 2)
    self.tp('Total plotting time {} s.'.format(end_time_plot))
    self.tp('Saving plot... This can take quite some time for PDF-files')
    ext = self.comboBox_well_plot_save_as.currentText()
    date = datetime.fromtimestamp(start_time).strftime('%Y%m%d-%H%M%S')
    fig_path = os.path.join(self.ce_dir_name, 'PlateOverview{}{}'.format(date, ext))
    fig_plot_wells.savefig(fig_path, dpi=300)
    plt.close(fig_plot_wells)
    self.tp('Plot saved to {}'.format(fig_path))
    end_time_save = round(time() - (start_time + end_time_plot), 2)
    self.tp('Total saving time {} s.\n'.format(end_time_save))
    return None


def plot_wells(well_labels, well_name, well_df, fig_plot_wells, xmin, xmax,
    ymin, ymax, well_colony_vertices, color_param):
    with plt.rc_context({'font.size': 5, 'axes.linewidth':0.3}):
        # Adding subplot here instead of preallocating with plt.subplots saves
        # time when the full plate is not used
        ax = fig_plot_wells.add_subplot(8, 12, well_labels.index(well_name)+1)
        # The cmap can always be specified, it gets ignored if colors are passed to c=.
        ax.scatter(well_df['LeftPixsize'], well_df['TopPixsize'],
            s = 0.09, marker = 'o', linewidths = 0.01, edgecolor = 'none',
            alpha = 0.6, c=color_param, cmap='inferno')
        ax.tick_params(bottom='off', top='off', left='off', right='off',
            labelbottom='off', labelleft='off')
        ax.set_title(well_name, fontsize = 4)
        # Set the axes min and max values
        ax.axis([xmin, xmax, ymin, ymax])
        # Colony outlines only if colonies have been clustered already
        if well_colony_vertices:
            for colony_name in well_df['Colony'].unique():
                if colony_name != '-1':
                    colony_vertices = well_colony_vertices['{}-{}'.format(
                        well_name, colony_name)]
                    ax.plot(colony_vertices[:, 0], colony_vertices[:, 1], lw=0.2)
    return fig_plot_wells


import matplotlib as mpl
from scipy.spatial import ConvexHull
import os
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def plot_colonies(self):
    #Change the default font size and axes linewidth for all plots
    mpl.rcParams['font.size'] = 5
    mpl.rcParams['axes.linewidth'] = .3
    #Create the fig at 1920 x 1080
#    my_dpi = 96 #FIXME Is the best way to set the fig to sceen size?
#    self.fig_well_patterning = plt.figure('WellPatterning', figsize=(1920/my_dpi, 1080/my_dpi), dpi=my_dpi)
    ax_subplot = self.fig_well_patterning.add_subplot(8,12,self.well_labels.index(self.well_name)+1) #the subplot must be created prior to setting the tight layout
    #This is to be able to access all the sublots afterwards. Not needed right now.
#    self.axes_well_patterning[self.well_num] = ax_subplot
#    ax_subplot = self.axes_well_patterning.flat[self.well_num]
    #Set the area of the figure that can be used by the plot
    self.fig_well_patterning.tight_layout(rect=[0.05,0,0.95,0.97]) #left, bottom, right, top
    #Maybe make the subplots flexible. Then ii cannot use a list for the wellabels
    ax_subplot.set_title(self.well_name + ' - ' + self.plate_layout[self.well_num] +
        ' (' + str(self.score) + ')', fontsize = 4)
    #Set the axes min and max values
    ax_subplot.axis([self.xmin, self.xmax, self.ymin, self.ymax])
    #Hide the tic marks leaving only a box around the cells
    ax_subplot.axes.get_xaxis().set_visible(False)
    ax_subplot.axes.get_yaxis().set_visible(False)
    #Color the cells differently depending on user input
    #Color according to binary code that is determined by all +/- combinations
    #of the thresholds
    if self.radioButton_thresholds.isChecked():
        #Thresholding with two channels
        if (self.checkBox_threshold_channel2.isChecked() and
            self.checkBox_threshold_channel3.isChecked()):
            #Maybe there is a nicer way to do this. At least it doesnt influence fig size.  Alpha does not seem to work
            self.fig_well_patterning.suptitle(os.path.basename(self.file_path),
                fontsize=6, fontstyle='normal', color='grey')
#            self.fig_well_patterning.suptitle('\n\nBig data points represent cells considered to be part of a colony, small points are cells outside colonies', color='black', alpha = 0.8)
            #Find the indexes for all the different combinations of the thresholds
            double_positive = np.where(
                (np.array(self.data.AvgIntenCh2.iloc[self.idx_cells_well]) >= self.threshold2) &
                (np.array(self.data.AvgIntenCh3.iloc[self.idx_cells_well]) >= self.threshold3))
            positive_negative = np.where(
                (np.array(self.data.AvgIntenCh2.iloc[self.idx_cells_well]) >= self.threshold2) &
                (np.array(self.data.AvgIntenCh3.iloc[self.idx_cells_well]) < self.threshold3))
            negative_positive = np.where(
                (np.array(self.data.AvgIntenCh2.iloc[self.idx_cells_well]) < self.threshold2) &
                (np.array(self.data.AvgIntenCh3.iloc[self.idx_cells_well]) >= self.threshold3))
            double_negative = np.where(
                (np.array(self.data.AvgIntenCh2.iloc[self.idx_cells_well]) < self.threshold2) &
                (np.array(self.data.AvgIntenCh3.iloc[self.idx_cells_well]) < self.threshold3))
            #Create a color matrix that holds the colors to the cells of the corresponding indices
            color = np.zeros((len(self.idx_cells_well),3))
            color[double_positive] = [1,0.2,0]
            color[positive_negative] = [0.8, 0, 0.8]
            color[negative_positive] = [0,0.75,1]
            color[double_negative] = [0.1, 0.1, 0.1]
            #Plot the cells at different transparency levels and with the color specified above
            plot_clustered = plt.scatter(
                self.data.LeftPixsize.values[self.idx_cells_well[self.labels != -1]],
                self.data.TopPixsize.values[self.idx_cells_well[self.labels != -1]],
                s = 0.09, c = color[self.labels != -1], marker = 'o',
                linewidths = 0.01, edgecolor = 'none', alpha = 0.6)
            plot_unclustered = plt.scatter(
                self.data.LeftPixsize.values[self.idx_cells_well[self.labels == -1]],
                self.data.TopPixsize.values[self.idx_cells_well[self.labels == -1]],
                s = 0.06, c = color[self.labels == -1], marker = 'o',
                linewidths = 0.01, edgecolor = 'none', alpha = 0.3)
            #Create custom artists to be shown in the legend
            artist_pospos = plt.Line2D((0,0), (0,0), color=[1, 0.2, 0], marker='o',
                markersize=1, linestyle='', markeredgecolor='none', alpha = 0.5)
            artist_posneg = plt.Line2D((0,0), (0,0), color=[0.8, 0, 0.8], marker='o',
                markersize=1, linestyle='', markeredgecolor='none', alpha = 0.5)
            artist_negpos = plt.Line2D((0,0), (0,0), color=[0,0.75,1], marker='o',
                markersize=1, linestyle='', markeredgecolor='none', alpha = 0.5)
            artist_negneg = plt.Line2D((0,0), (0,0), color=[0.1, 0.1, 0.1], marker='o',
                markersize=1, linestyle='', markeredgecolor='none', alpha = 0.5)
            #Create legend from custom artist/label lists
            leg = ax_subplot.legend(
                [artist_pospos, artist_posneg, artist_negpos, artist_negneg],
                ['Ch2+Ch3+', 'Ch2+Ch3-', 'Ch2-Ch3+', 'Ch2-Ch3-'], numpoints=1,
                ncol=4, fontsize=1.1, markerscale=0.75, loc='upper center',
                bbox_to_anchor = (0.5, 1.02), borderpad=0.5, handletextpad = 0.1)
            #Adjust the thickness of the legend frame
            fr = leg.get_frame()
            fr.set_lw(0.3)
        #Thresholding with one channel
        elif self.checkBox_threshold_channel2.isChecked():
            self.fig_well_patterning.suptitle(os.path.basename(self.file_path), color='grey')
            #Find the indexes for all the different combinations of the thresholds
            positive = np.where(
                np.array(self.data.AvgIntenCh2.iloc[self.idx_cells_well] >= self.threshold2))
            negative = np.where(
                np.array(self.data.AvgIntenCh2.iloc[self.idx_cells_well] < self.threshold2))
            #Create a matrix of the colors to the cells of the corresponding indices
            color = np.zeros((len(self.idx_cells_well),3))
            color[positive] = [1,0.2,0]
            color[negative] = [0.1, 0.1, 0.1]
            #Plot the cells at different transparency levels and with the color specified above
            plot_clustered = plt.scatter(
                self.data.LeftPixsize.values[self.idx_cells_well[self.labels != -1]],
                self.data.TopPixsize.values[self.idx_cells_well[self.labels != -1]],
                s = 0.09, c = color[self.labels != -1], marker = 'o', linewidths=None,
                edgecolor = 'none', alpha = 0.6)
            plot_unclustered = plt.scatter(
                self.data.LeftPixsize.values[self.idx_cells_well[self.labels == -1]],
                self.data.TopPixsize.values[self.idx_cells_well[self.labels == -1]],
                s = 0.06, c = color[self.labels == -1], marker = 'o', linewidths=None,
                edgecolor = 'none', alpha = 0.3)
            #Create custom artists to be shown in the legend
            artist_pos = plt.Line2D((0,0), (0,0), color=[1, 0.2, 0], marker='o',
                markersize=1, linestyle='', markeredgecolor='none', alpha = 0.5)
            artist_neg = plt.Line2D((0,0), (0,0), color=[0.1, 0.1, 0.1], marker='o',
                markersize=1, linestyle='', markeredgecolor='none', alpha = 0.5)
            #Create legend from custom artist/label lists
            leg = ax_subplot.legend([artist_pos,artist_neg], ['Ch2+', 'Ch2-'],
                numpoints=1, ncol=2, fontsize=1.1, markerscale=0.75, loc='upper center',
                bbox_to_anchor = (0.5, 1.02), borderpad=0.5, handletextpad = 0.1)
            fr = leg.get_frame()
            fr.set_lw(0.3)
        elif self.checkBox_threshold_channel3.isChecked():
            self.fig_well_patterning.suptitle(os.path.basename(self.file_path), color='grey')
            #Find the indexes for all the different combinations of the thresholds
            positive = np.where(
                np.array(self.data.AvgIntenCh3.iloc[self.idx_cells_well] >= self.threshold3))
            negative = np.where(
                np.array(self.data.AvgIntenCh3.iloc[self.idx_cells_well] < self.threshold3))
            #Create a matrix of the colors to the cells of the corresponding indices
            color = np.zeros((len(self.idx_cells_well),3))
            color[positive] = [1,0.2,0]
            color[negative] = [0.1, 0.1, 0.1]
            #Plot the cells at different transparency levels and with the color specified above
            plot_clustered = plt.scatter(
                self.data.LeftPixsize.values[self.idx_cells_well[self.labels != -1]],
                self.data.TopPixsize.values[self.idx_cells_well[self.labels != -1]],
                s = 0.09, c = color[self.labels != -1], marker = 'o',
                linewidths=None, edgecolor = 'none', alpha = 0.6)
            plot_unclustered = plt.scatter(
                self.data.LeftPixsize.values[self.idx_cells_well[self.labels == -1]],
                self.data.TopPixsize.values[self.idx_cells_well[self.labels == -1]],
                s = 0.06, c = color[self.labels == -1], marker = 'o',
                linewidths=None, edgecolor = 'none', alpha = 0.3)
            #Create custom artists to be shown in the legend
            artist_pos = plt.Line2D((0,0), (0,0), color=[1, 0.2, 0], marker='o',
                markersize=1, linestyle='', markeredgecolor='none', alpha = 0.5)
            artist_neg = plt.Line2D((0,0), (0,0), color=[0.1, 0.1, 0.1], marker='o',
                markersize=1, linestyle='', markeredgecolor='none', alpha = 0.5)
            #Create legend from custom artist/label lists
            leg = ax_subplot.legend([artist_pos,artist_neg], ['Ch3+', 'Ch3-'],
                numpoints=1, ncol=2, fontsize=1.1, markerscale=0.75, loc='upper center',
                bbox_to_anchor = (0.5, 1.02), borderpad=0.5, handletextpad = 0.1)
            fr = leg.get_frame()
            fr.set_lw(0.3)
    #Color cells after channel 2 intensity
    elif self.radioButton_channel2.isChecked():
#        ax_subplot.patch.set_facecolor('black')
        self.fig_well_patterning.suptitle(os.path.basename(self.file_path), fontsize=4, color='grey')
        self.fig_well_patterning.suptitle('\n\nEncircled cells have protein intensities above the channel2 threshold', fontsize=3, color='grey')
        #For clustered cells
        #Set the edgecolor to black if above the threshold and white if below
        edgecolor = 'none' #np.where(
#            self.data.AvgIntenCh2.iloc[self.idx_cells_well[self.labels != -1]] > self.threshold2, 'k', 'w')
        color = self.data.AvgIntenCh2.iloc[self.idx_cells_well[self.labels != -1]]
        #Plot cells in colonies with a opacity of 0.7 and a color value corresponding to their channel intensity in a hot colormap
        #Use vmin and vmax to have the threshold always represent the same color, preferebly in the shift from orange to yellow so that it is easy to detect
        plot_clustered = plt.scatter(
            self.data.LeftPixsize.values[self.idx_cells_well[self.labels != -1]],
            self.data.TopPixsize.values[self.idx_cells_well[self.labels != -1]],
            s = 0.09, c = color, cmap = plt.cm.hot, marker = 'o', linewidths=0.05,
            vmin = self.colorbar_min_array[self.file_num, 0], #The min of the colorscale
            vmax = self.colorbar_max_array[self.file_num, 0], #The max of the colorscale
            edgecolor = edgecolor, alpha = 0.6)
        #For unclustered cells, opacity = 0.3
        edgecolor = np.where(
            self.data.AvgIntenCh2.iloc[self.idx_cells_well[self.labels == -1]] > self.threshold2, 'k', 'w')
        color = self.data.AvgIntenCh2.iloc[self.idx_cells_well[self.labels == -1]]
        plot_unclustered = plt.scatter(
            self.data.LeftPixsize.values[self.idx_cells_well[self.labels == -1]],
            self.data.TopPixsize.values[self.idx_cells_well[self.labels == -1]],
            s = 0.06, c = color, cmap = plt.cm.hot, marker = 'o', linewidths=0.05,
            vmin = self.colorbar_min_array[self.file_num, 0], #The min of the colorscale
            vmax = self.colorbar_max_array[self.file_num, 0], #The max of the colorscale
            edgecolor = edgecolor, alpha = 0.3)
        #Create a new axis to be used by the colorbar
        axins1 = inset_axes(ax_subplot, width="50%", #of parent box width
            height="2.5%", loc=1, #one of several preset locations
            bbox_to_anchor=(-.01,.012,.7,1), #xpos, ypos, width, heigth in relation to the preset location
            bbox_transform=ax_subplot.transAxes, borderpad=0)
        #Create the colorbar
        cbar = plt.colorbar(plot_clustered, cax=axins1, orientation="horizontal",
            ticks=[self.colorbar_min_array[self.file_num, 0], self.threshold2, self.colorbar_max_array[self.file_num, 0]])
        #Set the properties of the ticks and their labels
        axins1.xaxis.set_ticks_position("top")
        cbar.ax.tick_params(axis='x', direction='inout', length=1, pad=-1, labelsize=1, width=0.2)
        cbar.ax.set_xticklabels([str(int(self.threshold2/20)),
            'Threshold\n' + str(int(self.threshold2)), str(int(self.threshold2/0.35))])
    #Color cells after channel 2 intensity
    elif self.radioButton_channel3.isChecked():
        self.fig_well_patterning.suptitle(os.path.basename(self.file_path), color='grey')
        self.fig_well_patterning.suptitle('\nEncircled cells have protein intensities above the channel3 threshold', color='grey')
        #Plot cells in colonies with a opacity of 0.7 and a color value corresponding to their channel intensity in a hot colormap
        edgecolor = np.where(self.data.AvgIntenCh3.iloc[self.idx_cells_well[self.labels != -1]] > self.threshold3, 'k', 'w')
        color = self.data.AvgIntenCh3.iloc[self.idx_cells_well[self.labels != -1]]
        plot_clustered = plt.scatter(
            self.data.LeftPixsize.values[self.idx_cells_well[self.labels != -1]],
            self.data.TopPixsize.values[self.idx_cells_well[self.labels != -1]],
            s = 0.09, c = color, cmap = plt.cm.hot, marker = 'o', linewidths=0.05,
            vmin = self.colorbar_min_array[self.file_num, 1], #The min of the colorscale
            vmax = self.colorbar_max_array[self.file_num, 1], #The max of the colorscale
            edgecolor = edgecolor, alpha = 0.6)
        #Plot cells in colonies with a opacity of 0.7 and a color value corresponding to their channel intensity in a hot colormap
        edgecolor = np.where(
            self.data.AvgIntenCh3.iloc[self.idx_cells_well[self.labels == -1]] > self.threshold3, 'k', 'w')
        color = self.data.AvgIntenCh3.iloc[self.idx_cells_well[self.labels == -1]]
        plot_unclustered = plt.scatter(
            self.data.LeftPixsize.values[self.idx_cells_well[self.labels == -1]],
            self.data.TopPixsize.values[self.idx_cells_well[self.labels == -1]],
            s = 0.06, c = color, cmap = plt.cm.hot, marker = 'o', linewidths=0.05,
            vmin = self.colorbar_min_array[self.file_num, 1], #The min of the colorscale
            vmax = self.colorbar_max_array[self.file_num, 1], #The max of the colorscale
            edgecolor = edgecolor, alpha = 0.3)
        #Create a new axis to be used by the colorbar
        axins1 = inset_axes(ax_subplot, width="50%", #of parent box width
            height="2.5%", loc=1, #one of several preset locations
            bbox_to_anchor=(-.01,.012,.7,1), #xpos, ypos, width, heigth in relation to the preset location
            bbox_transform=ax_subplot.transAxes, borderpad=0)
        #Create the colorbar
        cbar = plt.colorbar(plot_clustered, cax=axins1, orientation="horizontal",
            ticks=[self.colorbar_min_array[self.file_num, 1], self.threshold3, self.colorbar_max_array[self.file_num, 1]])
        #Set the properties of the ticks and their labels
        axins1.xaxis.set_ticks_position("top")
        cbar.ax.tick_params(axis='x', direction='inout', length=1, pad=-1, labelsize=1, width=0.2)
        cbar.ax.set_xticklabels([str(int(self.threshold3/20)), #TODO fix so that the colorbar optin in the gui works
            'Threshold\n' + str(int(self.threshold3)), str(int(self.threshold3/0.35))])


   #Calculate the convex hull points of each colony to be able to plot the perimeter outline later on in the parent function
    if self.checkBox_convex_hull.isChecked():
        for hull_points_idx, hull_points_array in enumerate(self.cells_in_colonies2):
#            if len(hull_points_array) > 2:
            #ConvexHull and Delauny needs at least three values, errors otherwise, maybe try/except instead?
            #Also, all cells cannot be of the same x or y coordinate. The convex hull
            #can only be drawn if there are 2 dimensions
            if len(hull_points_array) > 2 and np.all([
                    min(hull_points_array[:,0]) != max(hull_points_array[:,0]),
                    min(hull_points_array[:,1]) != max(hull_points_array[:,1])]):
                hull = ConvexHull(hull_points_array)
#should be able to get it to work with the vertices now in new scipy......
#                ax_subplot.plot(hull_points_array[hull.vertices,0], hull_points_array[hull.vertices,1], 'k-', lw=0.1)
                for simplex in hull.simplices: #Hull simplices are the indices for -cells_in_colonier- of the cells incuded in the convex hull
                    ax_subplot.plot(hull_points_array[simplex,0],
                        hull_points_array[simplex,1], 'k', linestyle = '-',
                             linewidth=0.05)
     #TODO probably remove the circles options, it is not really necessary, keep in comments maybe for troubleshooting
    #Plot the outlines for the theoretical perfectly circular colonies
    if self.checkBox_perfectly_circular.isChecked():
        for idx, perfectly_circular_colony in enumerate(self.perfectly_circular_colonies): #not for -1
            ax_subplot.add_artist(perfectly_circular_colony)

    return

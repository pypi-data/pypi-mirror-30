# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 21:21:43 2014
@author: Joel

Description:
Outputs histograms of the intensities of the channels. The threshold is marked
and it is easy to see if the threshold need to be adjusted in respective to
positive and negative controls.

"""

from PyQt5.QtWidgets import QProgressDialog, QLabel
from skimage.filters import threshold_otsu
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
from datetime import datetime
from PyQt5 import QtCore
import matplotlib as mpl
from time import time
import pandas as pd
import numpy as np
import subprocess
import sys
import os


def prep_histograms(self):
    '''
    Get parameters from the interface and setup the loop for plotting.
    Log data if specified. Save data in the end.
    '''
    self.tp('\nPlotting histograms...')
    start_time = time()
    hist_params = {}
    hist_params['col'] = self.comboBox_hist_col.currentText()
    # Making this an integer so that there are no decimal points in the files names.
    # Float precision is likely never required here anyways.
    hist_params['scale'] = self.comboBox_hist_scale.currentText()
    hist_params['same_y'] = self.checkBox_histograms_same_y.isChecked()
    if hist_params['same_y']:
        hist_params['ymax_list'] = []
    # Create a smaller object containing only the columns used in the plots
    plot_data = self.data[[hist_params['col'], 'Well', 'Condition']].copy()
    if hist_params['scale'] == 'log':
        plot_data[hist_params['col']] = plot_data[hist_params['col']].apply(lambda x: np.log10(x + 1))
    # Determine threshold value
    if self.lineEdit_threshold.text() == '':
        thresh_arr = plot_data[hist_params['col']].values
        low_quant, up_quant = np.percentile(thresh_arr, [1, 99])
        thresh_arr = thresh_arr[np.where((thresh_arr > low_quant) & (thresh_arr < up_quant))]
#         hist_params['threshold'] = threshold_otsu(plot_data[hist_params['col']].values)
        # It makes sense to have the threshold as an integer since our microscope
        # can't measure intensities with decimal precision.
        hist_params['threshold'] = round(threshold_otsu(thresh_arr), 2)
            # Format the number back from log exponent before setting the threshold
            # The reason for this is that it would be unexpected for the user to suddenly
            # have to specify the log exponent rather than the actual threshold value.
        if hist_params['scale'] == 'log':
#             self.lineEdit_threshold.setText(str(int(round(10**hist_params['threshold']))))
            self.tp('Automatic threshold: {}'.format(10**hist_params['threshold']))
        else:
#             self.lineEdit_threshold.setText(str(int(round(hist_params['threshold']))))
            self.tp('Automatic threshold: {}'.format(hist_params['threshold']))
    else:
        if hist_params['scale'] == 'log':
            hist_params['threshold'] = round(np.log10(float((self.lineEdit_threshold.text()))), 2)
        else:
            hist_params['threshold'] = float(self.lineEdit_threshold.text())
    # Automatic or manual axes limits
    # Use the 0.01 - 0.999 quantiles as the default x-axis range to prevent
    # unecessary stretching due to outliers that won't be visible anyways.
    if self.lineEdit_xmax.text() == '':
        hist_params['xmax'] = plot_data[hist_params['col']].quantile(0.999)
    else:
        hist_params['xmax'] = float(self.lineEdit_xmax.text())
    if self.lineEdit_xmin.text() == '':
        hist_params['xmin'] = plot_data[hist_params['col']].quantile(0.001)
    else:
        hist_params['xmin'] = float(self.lineEdit_xmin.text())

    # Plot loop, can't parallize due to matplotlib doing copy on write when the
    # same figure is passed to multiple processes. So each subplot ends up in
    # a separate figure.
    # TODO change the loop to conditions instead of wells. Need to check if the
    # wells are in the condition by default so that this can be the fallback
    my_dpi = 96
    fig_plot_histograms = plt.figure(figsize=(1920/my_dpi, 1080/my_dpi), dpi=my_dpi)
    # Since all float values can't be represented properly in binary, it is
    # quite the ordeal to round to two decimals and not get `.99999...`.
#     rounded_hist_params = {key:('{:.1f}'.format(round(value, 2)) if
#         isinstance(value, float) else value) for key, value in hist_params.items()}
    fig_plot_histograms.suptitle('Input data: {}\nParameters: {}'.format(
        self.file_path, sorted(hist_params.items())), fontsize=6, color='grey')
    self.tp('Well\tCells\tTime(s)')
    for well_name, well_df in plot_data.groupby('Well'):
        start_time_well = time()
        # Returning the figure is actually redundant, but it looks cleaner
        fig_plot_wells, hist_params = plot_histograms(self.well_labels,
            well_name, well_df, fig_plot_histograms, hist_params)
        end_time_well = round(time() - start_time_well, 2)
        self.tp('{}\t{}\t{}'.format(well_name, well_df.shape[0], end_time_well))
    if hist_params['same_y']:
        for ax in fig_plot_histograms.axes:
            ax.set_ylim(None, max(hist_params['ymax_list']))
    fig_plot_wells.tight_layout(h_pad=2, w_pad=3) #rect=[0.05,0,0.95,0.97])
    # Save
    end_time_plot = round(time() - start_time, 2)
    self.tp('Total plotting time {} s.'.format(end_time_plot))
    self.tp('Saving plot...')
    date = datetime.fromtimestamp(start_time).strftime('%Y%m%d-%H%M%S')
    fig_path = os.path.join(self.ce_dir_name, 'Histograms-{}-th{}-{}.pdf'.format(
        hist_params['col'], hist_params['threshold'], date))
    fig_plot_wells.savefig(fig_path)
    plt.close(fig_plot_wells)
    self.tp('Plot saved to {}'.format(fig_path))
    end_time_save = round(time() - (start_time + end_time_plot), 2)
    self.tp('Total saving time {} s.\n'.format(end_time_save))
    return None


def plot_histograms(well_labels, well_name, well_df, fig_plot_histograms, hist_params):
    with plt.rc_context({'font.size': 12, 'axes.linewidth':0.3, 'axes.edgecolor':'grey',
      'xtick.color':'grey', 'ytick.color':'grey'}):
        # Adding subplot here instead of preallocating with plt.subplots saves
        # time when the full plate is not used
        ax = fig_plot_histograms.add_subplot(8, 12, well_labels.index(well_name)+1)
        bins = 'auto' #if hist_params['scale'] =='linear' else np.logspace(
           #     np.log(well_df[hist_params['col']].min()), np.log(well_df[hist_params['col']].max()))
        hist_df = well_df[hist_params['col']]# if hist_params['scale'] =='linear' else well_df[hist_params['col']].apply(np.log10)
        # The cmap can always be specified, it gets ignored if colors are passed to c=.
        # TODO could use xmin and max t ocut the data justforr the plot to get the number of bins to look the same for all plots
        # hist_params['xmax'] = np.log(hist_params['xmax'])
        # hist_params['xmin'] = np.log(hist_params['xmin'])
        ax.hist(hist_df, histtype='stepfilled', alpha=0.6, bins=bins, color='r',linewidth = 0)
        #ax.set_xscale(hist_params['scale']) # Todo, look into making bins the same size http://stackoverflow.com/questions/6855710/how-to-have-logarithmic-bins-in-a-python-histogram
        # Plot a vertical line for where the threshod is
        ax.axvline(hist_params['threshold'], color='k', linestyle=':', lw=0.7)
        # Calculate and plot percentage of cells above and below the threshold
        percent_pos = '{} %'.format(round((well_df[hist_params['col']] >
            hist_params['threshold']).mean() * 100, 1))
        percent_neg = '{} %'.format(round((well_df[hist_params['col']] <
            hist_params['threshold']).mean() * 100, 1))
        ax.annotate(percent_pos, xy=(1,1), xycoords='axes fraction',
            fontsize = 3.5, horizontalalignment='right', verticalalignment='top',
            color='grey', xytext=(-0.5, -0.5), textcoords='offset points')
        ax.annotate(percent_neg, xy=(0, 1), xycoords='axes fraction',
            fontsize = 3.5, horizontalalignment='left', verticalalignment='top',
            color='grey', xytext=(0.5, -0.5), textcoords='offset points')
        # Format axes and ticks
        ax.set_xlim(hist_params['xmin'], hist_params['xmax'])
#         ax.tick_params(top='off', right='off', labelsize=3, pad=1,
#             labelbottom='on', labelleft='on')#, colors='grey')
        ax.tick_params(top='off', right='off', labelbottom='on', labelleft='on',
            pad=1, length=1, width=0.5, labelsize=3.5)#, colors='grey')
        ax.set_xlabel(hist_params['col'], labelpad=0, size=3.5, color='grey')
        ax.set_ylabel('Frequency', labelpad=0, size=3.5, color='grey')
        # Set title to condition instead of well name, but don't group by condition,
        # it is easier to always keep the subplot layout in 96 well format.
        condition = well_df.iat[0, well_df.columns.get_loc('Condition')]
        ax.set_title('{} ({:,} cells)'.format(condition, well_df.shape[0]), fontsize=4, y=0.95)
        ax.yaxis.set_major_locator(MaxNLocator(4))
        ax.xaxis.set_major_locator(MaxNLocator(5))
        #ax.get_xaxis().set_major_formatter(plt.LogFormatter(10,  labelOnlyBase=False))
        if hist_params['scale'] == 'log':
            ax.set_xticklabels(['10e{}'.format(round(x, 1)) for x in ax.get_xticks()])
        if hist_params['same_y']:
            hist_params['ymax_list'].append(ax.get_ylim()[1])
    return fig_plot_histograms, hist_params


def prep_scatter(self):
    self.tp('Plotting scatter plot...')
    self.tp('Well\tCells\tTime(s)')
    start_time = time()
    my_dpi = 96
    fig_plot_scatter = plt.figure(figsize=(1920/my_dpi, 1080/my_dpi), dpi=my_dpi)
    fig_plot_scatter.suptitle('{}\nThe parenthesis indicates the number of cells '
        'per well.\nThe '.format(os.path.basename(self.file_path)),
        fontsize=6, fontstyle='normal', color='grey')
    scatter_params = {}
    scatter_params['x_col'] = self.comboBox_scatter_col_x.currentText()
    scatter_params['x_threshold'] = int(self.lineEdit_scatter_threshold_x.text())
    scatter_params['x_scale'] = self.comboBox_scatter_scale_x.currentText()
    scatter_params['y_col'] = self.comboBox_scatter_col_y.currentText()
    scatter_params['y_threshold'] = int(self.lineEdit_scatter_threshold_y.text())
    scatter_params['y_scale'] = self.comboBox_scatter_scale_y.currentText()
    # Auto or manual axis limits
    if self.lineEdit_scatter_xmax.text() == '':
        scatter_params['x_max'] = self.data[scatter_params['x_col']].max()
        x_max = self.data[scatter_params['x_col']].max()
    else:
        scatter_params['x_max'] = float(self.lineEdit_scatter_xmax.text())
        x_max = int(self.lineEdit_scatter_xmax.text())
    if self.lineEdit_scatter_xmin.text() == '':
        scatter_params['x_min'] = self.data[scatter_params['x_col']].min()
        x_min = self.data[scatter_params['x_col']].min()
    else:
        scatter_params['x_min'] = float(self.lineEdit_scatter_xmin.text())
        x_min = int(self.lineEdit_scatter_xmin.text())
    if self.lineEdit_scatter_ymax.text() == '':
        scatter_params['y_max'] = self.data[scatter_params['y_col']].max()
        y_max = self.data[scatter_params['y_col']].max()
    else:
        scatter_params['y_max'] = float(self.lineEdit_scatter_ymax.text())
        y_max = int(self.lineEdit_scatter_ymax.text())
    if self.lineEdit_scatter_ymin.text() == '':
        scatter_params['y_min'] = self.data[scatter_params['y_col']].min()
        y_min = self.data[scatter_params['y_col']].min()
    else:
        scatter_params['y_min'] = float(self.lineEdit_scatter_ymin.text())
        y_min = int(self.lineEdit_scatter_ymin.text())
    self.plot_data = self.data.loc[
        (self.data[scatter_params['x_col']] <= x_max) &
        (self.data[scatter_params['x_col']] >= x_min) &
        (self.data[scatter_params['y_col']] <= y_max) &
        (self.data[scatter_params['y_col']] >= y_min)]

    for well_name, well_df in self.plot_data.groupby('Well'):
        start_time_well = time()
        # Returning the figure is actually redundant, but it looks cleaner
        fig_plot_wells = plot_scatter(self.well_labels, well_name, well_df,
            fig_plot_scatter, scatter_params, x_min, x_max, y_min, y_max,
            self.checkBox_scatter_colorbar.isChecked())
        end_time_well = round(time() - start_time_well, 2)
        self.tp('{}\t{}\t{}'.format(well_name, well_df.shape[0], end_time_well))
    fig_plot_wells.tight_layout(rect=[0.05,0,0.95,0.97])

    end_time_plot = round(time() - start_time, 2)
    self.tp('Total plotting time {} s.'.format(end_time_plot))
    self.tp('Saving plot... This can take quite some time for PDF-files')
    date = datetime.fromtimestamp(start_time).strftime('%Y%m%d-%H%M%S')
    fig_path = os.path.join(self.ce_dir_name, 'Scatter-{}-th{}-{}-th{}-{}.pdf'.format(
        scatter_params['x_col'], scatter_params['x_threshold'],
        scatter_params['y_col'], scatter_params['y_threshold'], date))
    fig_plot_wells.savefig(fig_path)
    plt.close(fig_plot_wells)
    self.tp('Plot saved to {}'.format(fig_path))
    end_time_save = round(time() - (start_time + end_time_plot), 2)
    self.tp('Total saving time {} s.\n'.format(end_time_save))
    return None


def plot_scatter(well_labels, well_name, well_df, fig_plot_scatter,
    scatter_params, x_min, x_max, y_min, y_max, plot_colorbar):
    # TODO confirm that log works well
    with plt.rc_context({'font.size': 12, 'axes.linewidth':0.3, 'axes.edgecolor':'grey',
      'xtick.color':'grey', 'ytick.color':'grey'}):
        # Adding subplot here instead of preallocating with plt.subplots saves
        # time when the full plate is not used
        ax = fig_plot_scatter.add_subplot(8, 12, well_labels.index(well_name)+1)
           #     np.log(well_df[scatter_params['col']].min()), np.log(well_df[scatter_params['col']].max()))
        # Much faster to create and render the PDFs when using `hist2d` intead of
        # plotting every single data point with `scatter`
        # TODO Consider moving to hexagonal bins
        histax = ax.hist2d(well_df[scatter_params['x_col']], well_df[scatter_params['y_col']], bins=100, cmin=1, cmap='inferno')
        ax.set_xscale(scatter_params['x_scale'])
        ax.set_yscale(scatter_params['y_scale'])

        ax.set_xlabel(scatter_params['x_col'], labelpad=0, size=3.5, color='grey')
        ax.set_ylabel(scatter_params['y_col'], labelpad=0, size=3.5, color='grey')
        # Calculate percentage of cells above and below the threshold
        # The rounding displays too many significant digits when using the
        # `.round()` method of the data frame, so using the round function instead
        percent_x_pos_y_pos = '{}%'.format(round(
            ((well_df[scatter_params['x_col']] > scatter_params['x_threshold']) &
            (well_df[scatter_params['y_col']] > scatter_params['y_threshold']))
            .mean() * 100, 1))
        percent_x_pos_y_neg = '{}%'.format(round(
            ((well_df[scatter_params['x_col']] > scatter_params['x_threshold']) &
            (well_df[scatter_params['y_col']] <= scatter_params['y_threshold']))
            .mean() * 100, 1))
        percent_x_neg_y_pos = '{}%'.format(round(
            ((well_df[scatter_params['x_col']] <= scatter_params['x_threshold']) &
            (well_df[scatter_params['y_col']] > scatter_params['y_threshold']))
            .mean() * 100, 1))
        percent_x_neg_y_neg = '{}%'.format(round(
            ((well_df[scatter_params['x_col']] <= scatter_params['x_threshold']) &
            (well_df[scatter_params['y_col']] <= scatter_params['y_threshold']))
            .mean() * 100, 1))
        # Add percentages to the plot
        ax.annotate(percent_x_pos_y_pos, xy=(1,1), xycoords='axes fraction',
            fontsize = 3.5, horizontalalignment='right', verticalalignment='top',
            color='grey', xytext=(-0.5, -0.5), textcoords='offset points')
        ax.annotate(percent_x_pos_y_neg, xy=(1,0), xycoords='axes fraction',
            fontsize = 3.5, horizontalalignment='right', verticalalignment='bottom',
            color='grey', xytext=(-0.5, 0.5), textcoords='offset points')
        ax.annotate(percent_x_neg_y_pos, xy=(0,1), xycoords='axes fraction',
            fontsize = 3.5, horizontalalignment='left', verticalalignment='top',
            color='grey', xytext=(0.5, -0.5), textcoords='offset points')
        ax.annotate(percent_x_neg_y_neg, xy=(0,0), xycoords='axes fraction',
            fontsize = 3.5, horizontalalignment='left', verticalalignment='bottom',
            color='grey', xytext=(0.5, 0.5), textcoords='offset points')

        # Plot vertical lines where the thresholds are
        ax.axhline(scatter_params['y_threshold'], color='mediumturquoise', ls=(1, [1, 1.5]), lw=0.8)
        ax.axvline(scatter_params['x_threshold'], color='mediumturquoise', ls=(1, [1, 1.5]), lw=0.8)

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        ax.tick_params(top='off', right='off', labelbottom='on', labelleft='on',
            pad=1, length=1, width=0.5, labelsize=3.5)#, colors='grey')
        ax.set_title('{} ({})'.format(well_name, well_df.shape[0]), fontsize = 4, y=0.95)

        ax.yaxis.set_major_locator(MaxNLocator(5))
        ax.xaxis.set_major_locator(MaxNLocator(5))

        if plot_colorbar:
            cbar = fig_plot_scatter.colorbar(histax[3], fraction=0.03, pad=0.005,
                aspect=60, format='%.0f', ax=ax)
            cbar.ax.tick_params(labelsize=3, left='off', right='off', pad=0.5)
            cbar.ax.set_ylabel('Cells/Pixel', rotation=270, size=3.5, labelpad=3, color='grey')
            cbar.ax.yaxis.set_major_locator(MaxNLocator(4))
            cbar.outline.set_visible(False)
    return fig_plot_scatter

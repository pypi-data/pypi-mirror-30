#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 15:42:00 2013
@author: Joel

Description:
Prepare the data for processing
    - Read in the spreadsheet
    - Prepare the format of the output spreadsheets
    - Prepare variables  to be used later
    - Find the most extreme cartesian coordinates for the cells in order to
        set the axes of the WellPatterning plots to the same min and max values
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_defaults(self):
    self.well_labels = [
        'A1', 'A2', 'A3', 'A4',	'A5',	'A6',	'A7',	'A8',	'A9',	'A10',	'A11',	'A12',
        'B1', 'B2', 'B3', 'B4',	'B5',	'B6',	'B7',	'B8',	'B9',	'B10',	'B11',	'B12',
        'C1', 'C2', 'C3', 'C4',	'C5',	'C6',	'C7',	'C8',	'C9',	'C10',	'C11',	'C12',
        'D1', 'D2', 'D3', 'D4',	'D5',	'D6',	'D7',	'D8',	'D9',	'D10',	'D11',	'D12',
        'E1', 'E2', 'E3', 'E4',	'E5',	'E6',	'E7',	'E8',	'E9',	'E10',	'E11',	'E12',
        'F1', 'F2', 'F3', 'F4',	'F5',	'F6',	'F7',	'F8',	'F9',	'F10',	'F11',	'F12',
        'G1', 'G2', 'G3', 'G4',	'G5',	'G6',	'G7',	'G8',	'G9',	'G10',	'G11',	'G12',
        'H1', 'H2', 'H3', 'H4',	'H5',	'H6',	'H7',	'H8',	'H9',	'H10',	'H11',	'H12',]
    self.fieldlookuptable = np.array([
        [57, 58, 59, 60, 61, 62, 63, 64, 65],
        [56, 31, 32, 33, 34, 35, 36, 37, 66],
        [55, 30, 13, 14, 15, 16, 17, 38, 67],
        [54, 29, 12,  3,  4,  5, 18, 39, 68],
        [53, 28, 11,  2,  1,  6, 19, 40, 69],
        [52, 27, 10,  9,  8,  7, 20, 41, 70],
        [51, 26, 25, 24, 23, 22, 21, 42, 71],
        [50, 49, 48, 47, 46, 45, 44, 43, 72],
        [81, 80, 79, 78, 77, 76, 75, 74, 73],])


def preprocessing(self):
    # Makes it easy to always reference 'Condition' when plotting elsewhere
    # instead of having to check if it is empty and then use the well labels
    if not 'Condition' in self.data.columns:
        self.data['Condition'] = self.data['Well']

    if self.spinBox_resolution.value() == 0:
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
    #Set pixsize to the value in the spinbox whether this was just calculated
    #or prespecified.
    #self.pixsize = self.spinBox_resolution.value()
    #self.pixsize=256
#     print(self.pixsize)
        # The given x and y coordinates from the cellomics instrument are relative to
    # each field. The below transforms the coordinates to be relative to each well
    # depending on which scanning pattern the user chose
    self.data['LeftPixsize'] = ''
    self.data['TopPixsize'] = ''
    x_coordinates = np.zeros(len(self.data))
    y_coordinates = np.zeros(len(self.data))
    self.tp('Computing well coordinates from field coordinates...')
    for field_num, field in enumerate(self.data.Field):
        x_coordinates[field_num] = np.where(self.fieldlookuptable == field)[0]
        y_coordinates[field_num] = np.where(self.fieldlookuptable == field)[1]
    self.data.TopPixsize = self.data.Top + self.pixsize * x_coordinates
    self.data.LeftPixsize = self.data.Left + self.pixsize * y_coordinates
    #self.data.TopPixsize = self.data.Y
    #self.data.LeftPixsize = self.data.X
    self.tp('Ready')

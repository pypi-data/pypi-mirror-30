# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 03 22:29:21 2013
@author: Joel

Description:
Main file. Calls the GUI and grabs the status of checkboxes and line edits.
Holds the outline for the analysis process.
"""
import os
import sys
import operator
from time import time
from numbers import Number
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5 import QtCore
from natsort import natsorted
from PyQt5.QtWidgets import (QMainWindow, QApplication, QProgressDialog,
    QLabel, QTableWidgetItem, QFileDialog)

# Import the interface layouts from the file created with the QtDesigner
# import .gui.context_explorer_design as context_explorer_design
# import .gui.visual_clustering_gui as visual_clustering_gui
from .gui import context_explorer_design
from .gui import visual_clustering_gui
# Import the necessary functions from my scripts
from .data_processing import preprocessing
from .data_processing import load_defaults
from .plot_colonies import plot_colonies
from .plot_colonies import plot_wells_solocpu
from .cluster_cells import cluster_cells_multicpu
from .visual_clustering import done
from .visual_clustering import plot_colonies_clustering
from .intensity_distributions import prep_histograms
from .intensity_distributions import prep_scatter
from .colony_overlays import prep_colony_overlays
# Import the settings from last time the program ran
# If the program is run for the first time, then skip this step as the settings
# file does not exist yet.
# When the compiled program looks for refs it looks in /library.zip first. If the
# settings file is present there, it won't load from anywhere else. Therefore,
# it is crucial to exclude the settings file in the py2exe setup script.
# If the program is started from the shortcut (as it most often will be), the
# path to the 'dist' directory where the settings file is kept  needs to be added
# to the system path. If the script is run from an itnerpreterer or the program
# is started from within the directory, this still works and just adds an empty
# path which does no harm.
sys.path.append(os.path.join(os.getcwd() + os.sep, 'dist'))
try:
    import context_explorer_settings as ces
except ImportError:
    pass
    #print('You are running ContextExplorer for the first time, have fun!')

class MainWindow(QMainWindow, context_explorer_design.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionExit.triggered.connect(self.close)
        self.pushButton_visual_clustering.clicked.connect(self.show_clustering_window)
        self.pushButton_plot_histograms.clicked.connect(lambda: prep_histograms(self))
        self.pushButton_plot_scatter.clicked.connect(lambda: prep_scatter(self))
        self.pushButton_agg_col_plot.clicked.connect(lambda: prep_colony_overlays(self))
        self.pushButton_clear_layout.clicked.connect(self.tableWidget_plate_layout.clear)
        self.pushButton_clear_layout.clicked.connect(self.update_plate_layout)
        self.pushButton_assign_layout.clicked.connect(self.update_plate_layout)
        # TODO Store the table widget and clipboard as variables, this is for the
        # keypress function but should also exist when the plate layout is typed
        # instead of pasted, i.e. no keypresses are made.
        self.table = self.tableWidget_plate_layout
        self.clip = QApplication.clipboard()
        # TODO update this when building on windows next time
        # Since the shortcut to the program is one folder higher than the program
        # itself, we need to switch to that folder. This is only true when running
        # the application from the shortcut and not from the executable or script,
        # so we check wether there is a subfoler with the name 'dist' and if it
        # exists, we switch to it. This causes all the settings to be loaded correctly
        if (os.path.basename(os.getcwd()) != 'dist' and
          os.path.isdir(os.getcwd() + os.sep + 'dist')):
            os.chdir(os.getcwd() + os.sep + 'dist')
        self.load_last_settings()
        load_defaults(self)
        # TODO go through and remove what is not necessary
        self.comboBox_scatter_scale_y.hide()
        self.comboBox_scatter_scale_x.hide()
        self.label_xmax_3.hide()
        self.label_xmax_4.hide()
        self.label_22.hide()
        self.label_32.hide()
        self.label_2.hide()
        # Hide the last 2 tabs.
        self.tabWidget.removeTab(self.tabWidget.count() - 1) # zero indexed
        self.tabWidget.removeTab(self.tabWidget.count() - 1)
        self.listWidget.hide()
        self.checkBox_no_plots.hide()
        self.checkBox_skip_coldetection.hide()
        self.pushButton_analyze.hide()
        plt.ioff() # turn off interactive plotting so that figures don't pop up
        self.pushButton_identify_colonies.clicked.connect(self.cluster_cells_multicpu_wrapper)
        self.pushButton_plot_wells.clicked.connect(lambda: plot_wells_solocpu(self))
        self.pushButton_update_well_plot_color.clicked.connect(self.update_well_plot_color)
        self.comboBox_well_plot_save_as.addItems(['.jpg', '.pdf', '.png'])
        self.comboBox_hist_scale.addItems(['linear', 'log'])
        self.comboBox_scatter_scale_x.addItems(['linear', 'log'])
        self.comboBox_scatter_scale_y.addItems(['linear', 'log'])
        self.comboBox_agg_level.addItems(['Colony', 'Condition'])
        # I use these lists of comboboxes in the `boolen_column` function
        self.boolean_comp_op_combos = [ # comparison operators
            self.comboBox_bool_comp_op_1, self.comboBox_bool_comp_op_2,
            self.comboBox_bool_comp_op_3, self.comboBox_bool_comp_op_4]
        for bool_comp_op in self.boolean_comp_op_combos:
            bool_comp_op.addItems(['>', '<', '=', '≠'])
        # Initialize `well_colony_vertices`, to avoid cumbersome if-expression later on
        self.well_colony_vertices = False
        self.pushButton_add_col_bool.clicked.connect(self.add_column)
        self.pushButton_add_col_apply.clicked.connect(self.add_column_apply)
        self.pushButton_delete_column.clicked.connect(self.delete_column)
        self.pushButton_rename_column.clicked.connect(self.rename_column)
        self.pushButton_delete_outside_cells.clicked.connect(self.delete_outside_cells)
        self.pushButton_view_data.clicked.connect(self.view_data)
        self.pushButton_save_data.clicked.connect(self.save_data)
        self.pushButton_save_agg_data.clicked.connect(self.save_agg_data)
        self.checkBox_bool_1.stateChanged.connect(self.change_bool_state_1)
        self.checkBox_bool_2.stateChanged.connect(self.change_bool_state_2)
        self.checkBox_bool_3.stateChanged.connect(self.change_bool_state_3)
        self.checkBox_bool_4.stateChanged.connect(self.change_bool_state_4)
        self.pushButton_view_col_data_types.clicked.connect(self.view_column_data_types)
        # `open_file` will always be the first action so just call it on startup
        self.open_file()

    def delete_column(self):
        col_to_delete = self.comboBox_delete_column.currentText()
        self.data = self.data.drop(col_to_delete, axis=1)
        self.tp('Deleted {}\n'.format(col_to_delete))
        self.update_column_combo_boxes()
        return None

    def rename_column(self):
        col_to_rename = self.comboBox_rename_column.currentText()
        new_col_name = self.lineEdit_new_col_name_rename.text()
        self.data = self.data.rename(columns={col_to_rename:new_col_name})
        self.tp('Renamed {} to {}\n'.format(col_to_rename, new_col_name))
        self.update_column_combo_boxes()
        self.lineEdit_new_col_name_rename.clear()
        return None

    def delete_outside_cells(self):
        if 'Colony' in self.data.columns:
            self.data = self.data.loc[self.data['Colony'] != '-1']
            self.tp('Cells deleted')
        else:
            self.tp('Cannot delete cells before colonies have been identified')
        return None

    def change_bool_state_1(self):
        if self.checkBox_bool_1.isChecked():
            self.comboBox_bool_col_1.setEnabled(True)
            self.comboBox_bool_comp_op_1.setEnabled(True)
            self.lineEdit_bool_value_1.setEnabled(True)
        else:
            self.comboBox_bool_col_1.setEnabled(False)
            self.comboBox_bool_comp_op_1.setEnabled(False)
            self.lineEdit_bool_value_1.setEnabled(False)
        return None

    def change_bool_state_2(self):
        if self.checkBox_bool_2.isChecked():
            self.comboBox_bool_col_2.setEnabled(True)
            self.comboBox_bool_comp_op_2.setEnabled(True)
            self.lineEdit_bool_value_2.setEnabled(True)
        else:
            self.comboBox_bool_col_2.setEnabled(False)
            self.comboBox_bool_comp_op_2.setEnabled(False)
            self.lineEdit_bool_value_2.setEnabled(False)
        return None

    def change_bool_state_3(self):
        if self.checkBox_bool_3.isChecked():
            self.comboBox_bool_col_3.setEnabled(True)
            self.comboBox_bool_comp_op_3.setEnabled(True)
            self.lineEdit_bool_value_3.setEnabled(True)
        else:
            self.comboBox_bool_col_3.setEnabled(False)
            self.comboBox_bool_comp_op_3.setEnabled(False)
            self.lineEdit_bool_value_3.setEnabled(False)
        return None

    def change_bool_state_4(self):
        if self.checkBox_bool_4.isChecked():
            self.comboBox_bool_col_4.setEnabled(True)
            self.comboBox_bool_comp_op_4.setEnabled(True)
            self.lineEdit_bool_value_4.setEnabled(True)
        else:
            self.comboBox_bool_col_4.setEnabled(False)
            self.comboBox_bool_comp_op_4.setEnabled(False)
            self.lineEdit_bool_value_4.setEnabled(False)
        return None

    def save_agg_data(self):
        self.tp('Saving...')
        date = datetime.fromtimestamp(time()).strftime('%Y%m%d-%H%M%S')
        agg_level = self.comboBox_agg_level.currentText()
        # TODO could include scipy.stats.sem, but not dependent on scipy at the
        # moment ( or maybe sklearn is alraedy?)
        # TODO The aggregation functions should be choosable in the future.
        # Just including the mean for now.
        agg_metrics = [np.mean] #, np.median, np.std]
        agg_path = os.path.join(self.ce_dir_name,
            'aggregated-data-{}-{}.csv'.format(agg_level, date))
        if agg_level == 'Colony':
            if 'Colony' in self.data.columns:
                agg_data = self.data.groupby(['Condition', 'Well', 'Colony']).agg(
                    agg_metrics).reset_index()
                agg_data.columns = [col[0] + col[1].capitalize() for col in
                    agg_data.columns.values]
                agg_data.to_csv(agg_path, index=False, float_format='%.2f')
            else:
                self.tp('Cannot save aggregated colony data before cells have '
                        'been clustered into colonies.')
                return None
        elif agg_level == 'Condition':
            if 'Condition' in self.data.columns:
                agg_data = self.data.groupby(['Condition']).agg(
                    agg_metrics).reset_index()
                agg_data.columns = [col[0] + col[1].capitalize() for col in
                    agg_data.columns.values]
                agg_data.to_csv(agg_path, index=False, float_format='%.2f')
            else:
                self.tp('Cannot save aggregated condition data before cells have '
                        'been assigned conditions in the plate layout')
                return None
        self.tp('Data saved to {}'.format(agg_path))
        return None

    def save_data(self):
        self.tp('Saving...')
        date = datetime.fromtimestamp(time()).strftime('%Y%m%d-%H%M%S')
        file_path = os.path.join(self.ce_dir_name, 'cell-data{}.csv'.format(date))
        self.data.to_csv(file_path, index=False, float_format='%.2f')
        self.tp('Data saved to {}'.format(file_path))
        return None

    def view_data(self):
        self.tp('Selected data:')
        # Negative values can be used to specify the last row
        row_min = self.spinBox_row_min.value()
        row_max = self.spinBox_row_max.value()
        if self.checkBox_view_data_all_cols.isChecked():
            col_name = self.data.columns
        else:
            col_name = self.comboBox_view_data_col.currentText()
        # Allow pandas to display the however many rows and cols are specified
        with pd.option_context("display.max_rows", self.data.shape[0],
            'display.max_columns', self.data.shape[1]):
            print('{}\n'.format(self.data[col_name].iloc[row_min:row_max]))
        return None

    def view_column_data_types(self):
        width = max([len(col) for col in self.data.columns]) + 5
        self.tp('Column data types:')
        for col in self.data.columns:
            # For mixed data
            if len(self.data[col].apply(type).unique()) > 1:
                print('{0: <{1}}mix of {2}({3})'.format(col, width, ' and '
                    .join(self.data[col].apply(lambda x: str(type(x))
                    .split("'")[1]).unique()), self.data[col].dtype))
            # All other cases have only 1 dtype so it is safe to check only 1 element
            elif isinstance(self.data[col][0], Number):
                print('{0: <{1}}number   ({2})'.format(col, width, str(self.data[col].dtype)))
            elif isinstance(self.data[col][0], str):
                print('{0: <{1}}text     ({2})'.format(col, width, str(self.data[col].dtype)))
            elif isinstance(self.data[col][0], np.bool_):
                print('{0: <{1}}boolean  ({2})'.format(col, width, str(self.data[col].dtype)))
            # For any other type of dtype
            else:
                print('{0: <{1}}{2} ({3})'.format(col, width, str(type(
                    self.data[col][0])).split("'")[1], self.data[col].dtype))
        print('')
        return None

    def add_column_apply(self):
        '''
        Evaluates a user expression and applies it to a column to create a new
        column with the results.
        '''
        # Discussions on how to make eval safer:
        # http://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
        # http://lybniz2.sourceforge.net/safeeval.html
        # "Of course in most cases (desktop programs) the user can't do any more
        # than they could do by writing their own python script, but in some
        # applications (web apps, kiosk computers), this could be a risk."
        # That quote has a valid point, the user can at most wreck their own
        # machine in my case, and only if they really try to. It was still
        # interesting to learn abotu eval safety issues.
        self.tp('Adding new column...')
        apply_str = self.lineEdit_transformation_apply.text()
        new_col_name = self.lineEdit_new_col_name_apply.text()
        apply_col = self.comboBox_add_col_apply.currentText()
        # Create a dictionary for builin functions
        safe_user_funcs = {'log10':np.log10, 'log2':np.log2, 'abs':abs, 'len':len}
        # Remove builtin functions and only offers acces to the explicity
        # specified supplied
        # The ** are for exapnding the items within those dictionaries and
        # combining it into a new dictionary with the surroundinf {}. This
        # is done since I can't specify `x` other than in the lambda expression.
        try:
            self.data[new_col_name] = self.data[apply_col].apply(lambda x: eval(
                apply_str, {'__builtins__':None}, {**safe_user_funcs, **{'x':x}}))
            self.update_column_combo_boxes()
            self.tp('Added column {}.\n'.format(new_col_name))
        except TypeError:
            self.tp('ERROR. Possible reasons:\n1.You are trying to perform a '
                ' numerical operation on a text column or vice versa. Check the '
                'column data types.\n2.You are trying to use an unknown function. '
                'The available functions are {}.\n'.format(
                ', '.join([func for func in safe_user_funcs])))
        except SyntaxError:
            self.tp('Expression syntax incorrect. Expression string empty?\n')
        self.lineEdit_new_col_name_apply.clear()
        return None

    def add_column(self):
        self.tp('Adding new column...')
        new_col_name = self.lineEdit_new_col_name.text()
        comp_list = []
        if self.checkBox_bool_1.isChecked():
            comp_list.append([self.comboBox_bool_col_1.currentText(),
                self.comboBox_bool_comp_op_1.currentText(),
                self.lineEdit_bool_value_1.text()])
        if self.checkBox_bool_2.isChecked():
            comp_list.append([self.comboBox_bool_col_2.currentText(),
                self.comboBox_bool_comp_op_2.currentText(),
                self.lineEdit_bool_value_2.text()])
        if self.checkBox_bool_3.isChecked():
            comp_list.append([self.comboBox_bool_col_3.currentText(),
                self.comboBox_bool_comp_op_3.currentText(),
                self.lineEdit_bool_value_3.text()])
        if self.checkBox_bool_4.isChecked():
            comp_list.append([self.comboBox_bool_col_4.currentText(),
                self.comboBox_bool_comp_op_4.currentText(),
                self.lineEdit_bool_value_4.text()])

        comp_op_dict = {'>': operator.gt, '<': operator.lt, '=': operator.eq,
            '≠': operator.ne}
        bool_results = []
        res_comb_df = pd.Series(np.ones(self.data.shape[0]), dtype=bool)
        self.tp('Condition:')
        for comp_col, comp_op, comp_value in comp_list:
            if comp_value == '':
                comp_value = '[Empty]'
            self.tp('{} {} {}'.format(comp_col, comp_op, comp_value))
            if comp_value.isdigit():
                comp_value = float(comp_value)
            try:
                res = comp_op_dict[comp_op](self.data[comp_col], comp_value)
            except TypeError:
                # Try to print a helpful error message
                width = len(comp_col) + 1
                # For mixed data
                if len(self.data[comp_col].apply(type).unique()) > 1:
                    comp_col_print = ('{0: <{1}}mix of {2} ({3})'
                        .format(comp_col, width, ' and '
                        .join(self.data[comp_col]
                        .apply(lambda x: str(type(x))
                        .split("'")[1]).unique()), self.data[comp_col].dtype))
                # All other cases have only 1 dtype so it is safe to check only 1 element
                elif isinstance(self.data[comp_col][0], Number):
                    comp_col_print = '{0: <{1}}number ({2})'.format(
                        comp_col, width, self.data[comp_col].dtype)
                elif isinstance(self.data[comp_col][0], str):
                    comp_col_print = '{0: <{1}}text ({2})'.format(
                        comp_col, width, self.data[comp_col].dtype)
                elif isinstance(self.data[comp_col][0], np.bool_):
                    comp_col_print = '{0: <{1}}boolean ({2})'.format(
                        comp_col, width, self.data[comp_col].dtype)
                # For any other dtype
                else:
                    comp_col_print = '{0: <{1}}{2} ({3})'.format(
                        comp_col, width, str(type(self.data[comp_col][0]))
                        .split("'")[1], self.data[comp_col].dtype)
                self.tp('ERROR: The values in the {0} column are of a different type '
                'than comparison value.'.format(comp_col))
                self.tp('Comparison value data type: {0: <{1}}{2}'.format(
                        comp_value, width, str(type(comp_value)).split("'")[1]))
                self.tp('          Column data type: {0}\n'.format(comp_col_print))
                break
            # Abbreviate True/False to facilitate use in figure legends
            res_comb_df = res_comb_df & res
            tf_res = ['T' if x else 'F' for x in res]
            bool_results.append(tf_res)

        # Only create the column if the comparison above was valid
        if 'res' in locals():
            bool_tuples = list(zip(*bool_results))
#             self.data[new_col_name] = bool_tuples
            # Compress tuples to facilitate use in figure legends
#             self.data[new_col_name] = self.data[new_col_name].str.join('')
            self.data[new_col_name] = res_comb_df
            self.tp('Added column {}.'.format(new_col_name))
            self.update_column_combo_boxes()
            # Save paramters so it is possible to keep track of what conditino
            # the True/False value in a column represents
            list_to_save = list_to_save = [('ColumnName', new_col_name)]
            list_to_save.extend([(x[0], x[2])  for x in comp_list])
            # Easier to make it into a data frame than including new imports
            # just to save this list.
            date = datetime.fromtimestamp(time()).strftime('%Y%m%d-%H%M%S')
            pd.DataFrame(list_to_save).to_csv(os.path.join(self.ce_dir_name,
                'add-column-params-{}.csv'.format(date)), header=False, index=False)
            del res # otherwise `res` is kept in `locals()` for the next runand ruins the conditional above
        self.lineEdit_new_col_name.clear()
        print('')
        return None

    def cluster_cells_multicpu_wrapper(self):
        self.cluster_params, self.well_colony_vertices = cluster_cells_multicpu(self)
        self.update_column_combo_boxes()
        return None

    def update_well_plot_color(self):
        # TODO eventually this should be autmated but due to poor desgin it is not
        # easy to do with PyQt. Must update this after every time a new column is
        # added to the dataframe...zzzz...
        # This is actually worse than updating everywhere since the last used column would still be here until clicked
        self.comboBox_well_plot_color.clear()
        self.comboBox_well_plot_color.addItems(self.data.columns)
        return None

    def tp(self, string):
        # TODO Change this to just return the modified string to print so that I can
        # keep using print in all functions.
        '''
        tp = time_print, prefaces the string with the current time.
        More convenient under self, so it needn't be passed around everywhere.
        '''
        current_time = datetime.now().strftime('[%H:%M:%S]')
        if string[0] == '\n':
            print('\n{} {}'.format(current_time, string[1:]))
        else:
            print('{} {}'.format(current_time, string))
        return None

    def update_plate_layout(self):
        self.plate_layout_dict = {}
        # Go through all rows and columns
        self.tp('\nUpdating plate layout...')
        for row, well_letter in zip(range(0,8), ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']):
            for col in range(0,12):
                # Append the values to the list. If there is an empty cell, move
                # on to the next.
                try:
                    self.plate_layout_dict[well_letter + str(col+1)] = str(self.table.item(row,col).text())
                except AttributeError:
                    self.plate_layout_dict[well_letter + str(col+1)] = ''
        # Restore the plate layout. Put it here sinece the clear button is connected to this function
        self.table.setVerticalHeaderLabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
        # Since the data_preprocessing already sets ['Condition'] = ['Well'], it
        # only need to be updated if the user has specified conditions
        if not all([plate_label == '' for plate_label in self.plate_layout_dict.values()]):
            self.data['Condition'] = self.data['Well'].apply(lambda x: self.plate_layout_dict[x])
        self.tp('Done')

    def load_last_settings(self):
        # Always define `default_dir`, allows for brevity in the `open_file` def
        self.default_dir = os.getcwd()
        # If the settings file has been imported
        if 'context_explorer_settings' in sys.modules.keys():
            if hasattr(ces, 'DefaultDirectory'):
                self.default_dir = ces.DefaultDirectory
            if hasattr(ces, 'EpsDistance'):
                self.lineEdit_epsilon.setText(str(ces.EpsDistance))
            if hasattr(ces, 'MaxColonyRoundness'):
                self.lineEdit_max_roundness.setText(str(ces.MaxColonyRoundness))
            if hasattr(ces, 'MaxColonySize'):
                self.lineEdit_max_size.setText(str(ces.MaxColonySize))
            if hasattr(ces, 'MaxColonyDensity'):
                self.lineEdit_max_density.setText(str(ces.MaxColonyDensity))
            if hasattr(ces, 'MinCOlonyRoundness'):
                self.lineEdit_min_roundness.setText(str(ces.MinColonyRoundness))
            if hasattr(ces, 'MinColonySize'):
                self.lineEdit_min_size.setText(str(ces.MinColonySize))
            if hasattr(ces, 'MinColonyDensity'):
                self.lineEdit_min_density.setText(str(ces.MinColonyDensity))
            if hasattr(ces, 'IQR'):
                self.lineEdit_iqr.setText(str(ces.IQR))

    def keyPressEvent(self, e):
        # This function must be named 'keyPressEvent'. It captures all keypresses
        # and checks if they meet any of the specific keypresses listed in the
        # if-conditions. e = event
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            selected = self.table.selectedRanges()
            # Enables copying into multiple cells of the QtTableWidget from excel and
            # tab separated text files.
            if e.key() == QtCore.Qt.Key_V:# paste
                first_row = selected[0].topRow()
                first_col = selected[0].leftColumn()
                # copied text is split by '\n' and '\t' to paste to the cells
                for r, row in enumerate(self.clip.text().split('\n')):
                    for c, text in enumerate(row.split('\t')):
                        self.table.setItem(first_row+r, first_col+c, QTableWidgetItem(text))
                 # Resize the column width to fit the names of the conditions.
                self.table.resizeColumnsToContents()

                # TODO take the below away when i know everything exists as
                self.plate_layout = []
                # Go through all rows and columns
                for row in range(0,8):
                    for col in range(0,12):
                        # Append the values to the list. If there is an empty cell, move
                        # on to the next.
                        try:
                            self.plate_layout.append(str(self.table.item(row,col).text()))
                        except AttributeError:
                            self.plate_layout.append("")
                # Filter out empty items from the list. Some empty cells seems to be read to
                # the list and not filtered in the previous step so that is why this is needed.
#                self.plate_layout = [item for item in self.plate_layout if item != '']
                # Set the dictionary key of the currently selected item to the current plate layout
#                self.all_plate_layouts[str(self.listWidget.currentItem().text())] = self.plate_layout
#                print(self.plate_layout)
            # This is to copy from the table to somewhere else. Will probably not
            # be used that much
            elif e.key() == QtCore.Qt.Key_C: # copy
                s = ""
                for r in range(selected[0].topRow(),selected[0].bottomRow()+1):
                    for c in range(selected[0].leftColumn(),selected[0].rightColumn()+1):
                        try:
                            s += str(self.table.item(r,c).text()) + "\t"
                        except AttributeError:
                            s += "\t"
                    s = s[:-1] + "\n" # eliminate last '\t'
                self.clip.setText(s)

    def show_clustering_window(self):
        # Open the window. When no file is selected, print an error message
        if self.file_path == '':
            self.tp("No file selected. Open a file and select it in the list")
        else:
            # Assign the ClusteringWindow class to a variable (self.clustering_window)
            # in the main window of the application.
            # Values from the clustering window can be reached even after it is closed
            # by typing for example:
            # self.clustering_window.doubleSpinBox_distance.value()
            self.clustering_window = ClusteringWindow(self)
            # Display the window as a non-modal dialog. To display as a modal dialog,
            # use 'exec_' instead of 'show'.
            self.clustering_window.show()
            self.clustering_window.data_cluster = self.data.copy()
            self.clustering_window.spinBox_resolution.setValue(256)
            self.clustering_window.spinBox_resolution.setKeyboardTracking(False)
            self.clustering_window.spinBox_resolution.valueChanged.connect(lambda: plot_colonies_clustering(self))
            # Set the eps and minPts parameters to the ones in the main GUI.
            self.clustering_window.doubleSpinBox_distance.setValue(
                float(self.lineEdit_epsilon.text()))
            self.clustering_window.doubleSpinBox_min_points.setValue(
                float(self.lineEdit_min_pts.text()))
            # Set the sliders to these values as well
            self.clustering_window.horizontalSlider_distance.setValue(
                float(self.lineEdit_epsilon.text()))
            self.clustering_window.horizontalSlider_min_points.setValue(
                float(self.lineEdit_min_pts.text()))
            # Set the min and max size to the values in the GUI
            self.clustering_window.lineEdit_min_density.setText(
                str(self.lineEdit_min_density.text()))
            self.clustering_window.lineEdit_max_density.setText(
                str(self.lineEdit_max_density.text()))
            self.clustering_window.lineEdit_min_roundness.setText(
                str(self.lineEdit_min_roundness.text()))
            self.clustering_window.lineEdit_max_roundness.setText(
                str(self.lineEdit_max_roundness.text()))
            self.clustering_window.lineEdit_min_size.setText(
                str(self.lineEdit_min_size.text()))
            self.clustering_window.lineEdit_max_size.setText(
                str(self.lineEdit_max_size.text()))
#            self.clustering_window.lineEdit_ch1_min.setText(
#                str(self.lineEdit_ch1_min.text()))
#            self.clustering_window.lineEdit_ch1_max.setText(
#                str(self.lineEdit_ch1_max.text()))
#            self.clustering_window.lineEdit_ch2_min.setText(
#                str(self.lineEdit_ch2_min.text()))
#            self.clustering_window.lineEdit_ch2_max.setText(
#                str(self.lineEdit_ch2_max.text()))
#            self.clustering_window.lineEdit_ch3_min.setText(
#                str(self.lineEdit_ch3_min.text()))
#            self.clustering_window.lineEdit_ch3_max.setText(
#                str(self.lineEdit_ch3_max.text()))
            # Redraw plot when enter is pressed in a filter value box
            self.clustering_window.lineEdit_min_density.returnPressed.connect(
                lambda: plot_colonies_clustering(self))
            self.clustering_window.lineEdit_max_density.returnPressed.connect(
                lambda: plot_colonies_clustering(self))
            self.clustering_window.lineEdit_min_roundness.returnPressed.connect(
                lambda: plot_colonies_clustering(self))
            self.clustering_window.lineEdit_max_roundness.returnPressed.connect(
                lambda: plot_colonies_clustering(self))
            self.clustering_window.lineEdit_min_size.returnPressed.connect(
                lambda: plot_colonies_clustering(self))
            self.clustering_window.lineEdit_max_size.returnPressed.connect(
                lambda: plot_colonies_clustering(self))
#            self.clustering_window.lineEdit_ch1_min.returnPressed.connect(
#                lambda: plot_colonies_clustering(self))
#            self.clustering_window.lineEdit_ch1_max.returnPressed.connect(
#                lambda: plot_colonies_clustering(self))
#            self.clustering_window.lineEdit_ch2_min.returnPressed.connect(
#                lambda: plot_colonies_clustering(self))
#            self.clustering_window.lineEdit_ch2_max.returnPressed.connect(
#                lambda: plot_colonies_clustering(self))
#            self.clustering_window.lineEdit_ch3_min.returnPressed.connect(
#                lambda: plot_colonies_clustering(self))
#            self.clustering_window.lineEdit_ch3_max.returnPressed.connect(
#                lambda: plot_colonies_clustering(self))
            self.clustering_window.doubleSpinBox_min_points.valueChanged.connect(
                lambda: plot_colonies_clustering(self))
            self.clustering_window.doubleSpinBox_distance.valueChanged.connect(
                lambda: plot_colonies_clustering(self))
            # Connect all the buttons to their respective functions
            # One way to pass an argument with a function in a button connect, is to
            # use lambda. Anotehr is with button1.clicked.connect(partial(self.on_button, 1))
            # See http://eli.thegreenplace.net/2011/04/25/passing-extra-arguments-to-pyqt-slot/
            # Dont really need this plot button, just plot automatically from the beginning
    #        self.clustering_window.pushButton_plot.clicked.connect(lambda: plot_colonies_clustering(self))
            # Populate the spin box with the values of all the wells in the data set.
            self.clustering_window.comboBox_wells.addItems(
                natsorted(self.clustering_window.data_cluster['Well']
                    .astype(str)
                    .unique()))
            # Replot when the well in the spinbox is changed.
            self.clustering_window.comboBox_wells.activated.connect(
                lambda: plot_colonies_clustering(self))
            # Same as for the well slider for the slider controlling the color
            self.clustering_window.comboBox_color.addItems(
                natsorted(self.clustering_window.data_cluster
                    .select_dtypes([np.number])
                    .columns))
            self.clustering_window.comboBox_color.activated.connect(
                lambda: plot_colonies_clustering(self))

            # Link the sliders to the spinboxes so that one updates when the value
            # is changed in the other.
            self.clustering_window.horizontalSlider_distance.valueChanged.connect(
                self.clustering_window.doubleSpinBox_distance.setValue)
            self.clustering_window.horizontalSlider_min_points.valueChanged.connect(
                self.clustering_window.doubleSpinBox_min_points.setValue)
            # Turning off keyboard tracking causes the signal only to be omitted when
            # enter is pressed, focus is lost or arrows are clicked.
            self.clustering_window.doubleSpinBox_distance.setKeyboardTracking(False)
            self.clustering_window.doubleSpinBox_min_points.setKeyboardTracking(False)
            self.clustering_window.doubleSpinBox_distance.valueChanged.connect(
                self.clustering_window.horizontalSlider_distance.setValue)
            self.clustering_window.doubleSpinBox_min_points.valueChanged.connect(
                self.clustering_window.horizontalSlider_min_points.setValue)
            self.clustering_window.doubleSpinBox_top_edge.setKeyboardTracking(False)
            self.clustering_window.doubleSpinBox_bottom_edge.setKeyboardTracking(False)
            self.clustering_window.doubleSpinBox_left_edge.setKeyboardTracking(False)
            self.clustering_window.doubleSpinBox_right_edge.setKeyboardTracking(False)
            self.clustering_window.doubleSpinBox_top_edge.valueChanged.connect(
                lambda: plot_colonies_clustering(self))
            self.clustering_window.doubleSpinBox_bottom_edge.valueChanged.connect(
                lambda: plot_colonies_clustering(self))
            self.clustering_window.doubleSpinBox_left_edge.valueChanged.connect(
                lambda: plot_colonies_clustering(self))
            self.clustering_window.doubleSpinBox_right_edge.valueChanged.connect(
                lambda: plot_colonies_clustering(self))
            # Replot when the sliders are moved (and since they are linked also when
            # the value in the spinboxes change.
            self.clustering_window.horizontalSlider_distance.valueChanged.connect(
                lambda: plot_colonies_clustering(self))
            self.clustering_window.horizontalSlider_min_points.valueChanged.connect(
                lambda: plot_colonies_clustering(self))
            # Set the layout to the matplotlib widget canvas to tight.
            self.clustering_window.widget_matplotlib.canvas.fig.tight_layout()
            self.clustering_window.pushButton_done.clicked.connect(lambda: done(self))
            # Run the plot function as the window opens.
            plot_colonies_clustering(self)
        return None

    def update_column_combo_boxes(self):
        '''
        Refill the column list for all comboboxes. Should be run every time a
        new column is added/deleted to the data frame and when a new data frame
        is loaded.
        '''
        all_columns_combos = [self.comboBox_well_plot_color,
            self.comboBox_bool_col_1, self.comboBox_bool_col_2,
            self.comboBox_bool_col_3, self.comboBox_bool_col_4,
            self.comboBox_view_data_col, self.comboBox_delete_column,
            self.comboBox_add_col_apply, self.comboBox_rename_column]
        all_columns = self.data.columns.sort_values()
        for combo_box in all_columns_combos:
            previous_item = combo_box.currentText()
            combo_box.clear()
            combo_box.addItems(all_columns)
            # If the previous item has been removed, this gracefully selects the next
            combo_box.setCurrentText(previous_item)
        # Numerical only
        numerical_columns_combos =[self.comboBox_hist_col,
            self.comboBox_scatter_col_x, self.comboBox_scatter_col_y,
            self.comboBox_agg_col_line_x, self.comboBox_agg_col_line_y,
            self.comboBox_agg_col_hb_y, self.comboBox_agg_col_hb_x,
            self.comboBox_agg_col_hb_color]
        numerical_columns = [col for col in self.data.columns.sort_values() if
            self.data[col].dtype == int or self.data[col].dtype == float]
        for combo_box in numerical_columns_combos:
            previous_item = combo_box.currentText()
            combo_box.clear()
            combo_box.addItems(numerical_columns)
            # If the previous item has been removed, this gracefully selects the next
            combo_box.setCurrentText(previous_item)
        return None

    def standardize_well_names(self, well_str):
        '''
        Standardize well names by removing leading zeros (A01 --> A1)
        '''
        if well_str[1] == '0':
            return well_str[0] + well_str[2]
        else:
            return well_str

    def open_file(self):
        '''
        Read the selected csv-file into a pandas data frame.
        '''
        # All that is needed for multiple files is to add an "s": getOpenFileNames
        self.file_path = QFileDialog.getOpenFileName(self, "Open File Dialog",
            directory = self.default_dir, filter = "CSV-files (*.csv)")[0]
#        self.file_path = '/home/joel/edu/phd/spatial-state-transitions/jo30-fn-geltrex-gelatin/data/p1-30h/ce-test.csv'
        if self.file_path == '':
            self.tp('No file selected')
            self.label_open_file.setText('No file selected')
        else:
            self.tp('Loading data...')
            # MUCH faster to have the separator fixed and allow only for csv-files
            self.data = pd.read_csv(self.file_path, engine='c', sep=',', skipinitialspace=True)
            # Drop any columns without values
            self.data.dropna(inplace=True, axis=1, how='all')
            self.label_open_file.setText(self.file_path)
            self.tp('Loaded {}'.format(self.file_path))
            # Create a directory for all the analyses files
            base_name = os.path.basename(os.path.splitext(self.file_path)[0])
            dir_name = os.path.dirname(os.path.splitext(self.file_path)[0])
            self.ce_dir_name = os.path.join(dir_name, 'CE-{}'.format(base_name))
            if not os.path.exists(self.ce_dir_name):
                os.mkdir(self.ce_dir_name)
            self.data = self.data.rename(columns={'WellId': 'Well',
               'FieldNumber':'Field', 'XCentroid': 'Left', 'YCentroid': 'Top'})
            self.data['Well'] = self.data['Well'].apply(self.standardize_well_names)
            preprocessing(self)
            # Don't replace the default directory with an empty line if the user cancels the open dialogue
            if not self.file_path == []:
                # Save the settings as soon as the open file dialog is closed so that the
                # new directory is opened were the 'open' button to be clicked again
                self.default_dir = os.path.dirname(self.file_path)
            # Clear the plate layout when a new file is opened
#            self.tableWidget_plate_layout.clear()
            # Restore the labels on the headers
            self.table.setVerticalHeaderLabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
            # Reset the field resolution value so that it is recalculated later and not
            # mistaken for user input, which prevents the calculation
            self.spinBox_resolution.setValue(0) # TODO necessary?
            self.update_column_combo_boxes()
        return None


class ClusteringWindow(QMainWindow, visual_clustering_gui.Ui_MainWindow):
    """Customization for Qt Designer created window"""
    def __init__(self, MainWindow):
        # initialization of the superclass
        super().__init__()
        # setup the GUI --> function generated by pyuic4
        self.setupUi(self)


def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
    return None

if __name__ == '__main__':
    main()

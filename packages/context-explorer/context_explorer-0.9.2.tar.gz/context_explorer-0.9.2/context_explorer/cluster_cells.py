#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 14:46:10 2013
@author: joel

Description:
Cluster cells in colonies based on their density. The algorithm used is DBSCAN
as implemented in scikit-learn.
http://scikit-learn.org/stable/auto_examples/cluster/plot_dbscan.html#example-cluster-plot-dbscan-py
"""

#from sklearn.cluster import DBSCAN
#from joblib import Parallel, delayed

from time import time
from datetime import datetime
import numpy as np
import pandas as pd
from shapely.geometry import Point
from sklearn.cluster import DBSCAN
from joblib import Parallel, delayed
from scipy.spatial import ConvexHull
from shapely.geometry import MultiPoint


def cluster_cells_multicpu(self):
        '''
        Uses joblib to distribute colony identification over all the
        machine's CPUs. `self.data` is updated within this function,
        so there is no return variable.
        '''
        start_time = time()
        self.tp('Clustering cells in colonies...')
        self.tp('Well' + '\t' + 'Cells' + '\t' + 'Colonies' + '\t' + 'Time(s)')
        # Record all the params specified in the gui
        cluster_params = {}
        cluster_params['eps'] = float(self.lineEdit_epsilon.text())
        cluster_params['min_samples'] = float(self.lineEdit_min_pts.text())
        cluster_params['min_size'] = float(self.lineEdit_min_size.text())
        cluster_params['max_size'] = float(self.lineEdit_max_size.text())
        cluster_params['min_density'] = float(self.lineEdit_min_density.text())
        cluster_params['max_density'] = float(self.lineEdit_max_density.text())
        cluster_params['min_roundness'] = float(self.lineEdit_min_roundness.text())
        cluster_params['max_roundness'] = float(self.lineEdit_max_roundness.text())
        # MultiCPU clustering, -2 = all but one CPU. Change to 1 for debugging.
        results = Parallel(n_jobs=-2)(delayed(cluster_cells_dbscan) # Function
            (tp, well_name, well_df.copy(), cluster_params) # Arguments
            for well_name, well_df in self.data.groupby('Well')) # Loop to parallelize
        well_slices, well_colony_vertices_list = zip(*results)
        # Create a flat dict from the nested list of results
        # dict[well-colony]: colony_vertices
        well_colony_vertices = {}
        for multicpu_iteration in well_colony_vertices_list:
            for well_colony_tuple in multicpu_iteration:
                well_colony_vertices['{}-{}'.format(
                    well_colony_tuple[0], well_colony_tuple[1])] = well_colony_tuple[2]

        data_with_colonies = pd.concat(well_slices)
        self.data = data_with_colonies.sort_index() # Cores don't complete in order
        # The colony value is used as a label, so it needs to be converted from
        # int to string to be included in the population of the appropritate
        # comboboxes
        self.data['Colony'] = self.data['Colony'].astype(str)
        self.tp('Total clustering time {} s\n.'.format(round(time() - start_time, 2)))
        # TODO Need to write the return values to a file for reference
        # Probably just call a save function here
        return cluster_params, well_colony_vertices


def cluster_cells_dbscan(tp, well_name, well_df, cluster_params):
    '''Use DBSCAN to identify density connected clusters of data points.'''
    start_time = time()
    # The actual classification is just two lines
    clf = DBSCAN(eps=cluster_params['eps'], min_samples=cluster_params['min_samples'])
    db_res = clf.fit(well_df[['LeftPixsize', 'TopPixsize']])

    well_df['Colony'] = db_res.labels_
    well_df['Colony'] = well_df['Colony'].astype(object)
    well_colony_vertices_list = []
    colony_dfs_list = []
    # With sort=False, the index will be kept in the original order and don't need sorting after
    for colony_name, colony_df in well_df.groupby('Colony', sort=False):
        # Only need to pass the copy to the first function, since colony_df orignally
        # is an implicit copy from the groupby operation
        colony_df, colony_size, colony_name = filter_colony_size(colony_df.copy(),
            cluster_params, colony_name)
        if colony_name != -1:
            colony_df, colony_props = compute_colony_properties(colony_df, colony_size)
            # Must calculate colony props before filtering on them
            colony_df = filter_colony_properties(colony_df, cluster_params, colony_props)
            well_colony_vertices_list.append((well_name, colony_name, colony_props['vertices']))
        colony_dfs_list.append(colony_df)

    well_df = pd.concat(colony_dfs_list)
    final_time = round(time() - start_time, 2)
    tp('{}\t{}\t{}\t{}'.format(well_name, well_df.shape[0],
        well_df.loc[well_df['Colony'] != -1, 'Colony'].unique().size, final_time))
    return well_df, well_colony_vertices_list


def tp(string):
    '''Only including this here, since passing `self` to the multiCPU call throws
    a QtGuiClipboard error, so there is not way of passing `self.tp` to
    `cluster_cells_dbscan`.
    '''
    current_time = datetime.now().strftime('[%H:%M:%S]')
    print('{} {}'.format(current_time, string))


def compute_colony_properties(colony_df, colony_size):
    '''Compute the convex hull of the clusters and its geometrical properties.'''
    colony_props = {}
    # Assign variables so that each calculation is only made once per df/colony,
    # instead of once per row in the df/cell
    colony_props['hull'] = ConvexHull(np.asarray([colony_df['LeftPixsize'],
        colony_df['TopPixsize']]).T)
    # These methods are named unintuitively for 2d hulls
    colony_props['area'] = colony_props['hull'].volume
    colony_props['perimeter'] = colony_props['hull'].area
    colony_props['density'] = colony_size / colony_props['area']
    # From here and elsewhere http://gis.stackexchange.com/a/85820
    # This is 1 for a circle
    # TODO compae this to a area ratio, polygon to circle with the same radius
    colony_props['roundness'] = (colony_props['area'] /
        colony_props['perimeter']**2) * 4 * np.pi
    # Assign to all cells (redundant but don't want a new colony dataframe atm)
    # TODO potentially make a separate colony data frame and index like sql join tables
    # Easy to just groupby colony in the end to get it
    colony_df['Size'] = colony_size
    colony_df['ColonyArea'] = colony_props['area']
    colony_df['ColonyPerimeter'] = colony_props['perimeter']
    colony_df['ColonyDensity'] = colony_props['density'] # TODO * 10**6?? for better units
    colony_df['ColonyRoundness'] = colony_props['roundness']
    # These must be calculated once to use in the colony parameter optimization
    # which is fine, since they would only ever be used there for debugging.
    colony_polygon = MultiPoint(colony_props['hull'].points[
        colony_props['hull'].vertices]).convex_hull #13s, same as without
    pts = [Point(xy) for xy in zip(colony_df['LeftPixsize'], colony_df['TopPixsize'])] #21s
    colony_df['DistBorder'] = [colony_polygon.exterior.distance(p) for p in pts] #32s
    # These 2 lines only takes half the time of calling colony_polygon.centroid.distance #36s
    cent = np.array(colony_polygon.centroid)
    colony_df['DistCentroid'] = [np.linalg.norm(cent - p) for p in
        colony_df[['LeftPixsize', 'TopPixsize']].values]
    # colony_df['DistCentroid'] = [colony_polygon.centroid.distance(p) for p in pts] #43s
    # Normalizing enables cells to be classified as edge or centre independent
    # of colony size. Normalize to colony diameter, aka longest cross-section.
    norm_centroid = colony_df['DistCentroid'].max() - colony_df['DistCentroid'].min()
    colony_df['NormDistCentroid'] = colony_df['DistCentroid'] / norm_centroid
    # Normalize to longest distance to the closest border, aka will only be
    # the same as colony diameter when the polygon is a circle, otherwise less.
    norm_border = colony_df['DistBorder'].max() - colony_df['DistBorder'].min()
    colony_df['NormDistBorder'] = colony_df['DistBorder'] / norm_border
    # Calculate xy-coorditanes to use in hexbin plots
    colony_df['XRelativeCentroid'] = colony_df['LeftPixsize'] - cent[0]
    colony_df['YRelativeCentroid'] = colony_df['TopPixsize'] - cent[1]
    # Store the vertices separate since they will only be used for plotting
    colony_props['vertices'] = (colony_df[['LeftPixsize', 'TopPixsize']]
        .iloc[colony_props['hull'].vertices].values)
    colony_props['vertices'] = np.vstack((colony_props['vertices'],
        colony_props['vertices'][0]))
    return colony_df, colony_props


def filter_colony_size(colony_df, cluster_params, colony_name):
    '''Assign -1 label to too small and too large colonies.'''
    colony_size = colony_df.shape[0] #TODO check that the minimum size boxes in the GUI can never be set to less than 3for qhull to work correctly
    if not cluster_params['min_size'] < colony_size < cluster_params['max_size']:
        colony_df['Colony'] = -1
        colony_name = -1
    return colony_df, colony_size, colony_name


def filter_colony_properties(colony_df, cluster_params, colony_props):
    '''Assign -1 label to clusters not meeting these criteria'''
    # TODO add area and perimeter? Or unnecessary with too many filters?
    if not cluster_params['min_density'] < colony_props['density'] < cluster_params['max_density']:
          colony_df['Colony'] = -1
    if not cluster_params['min_roundness'] < colony_props['roundness'] < cluster_params['max_roundness']:
          colony_df['Colony'] = -1
    return colony_df

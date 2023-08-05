.. ContextExplorer documentation master file, created by
   sphinx-quickstart on Wed Mar 14 14:03:28 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ContextExplorer
###############

Thanks for stopping by! ``（ ^_^）o自自o（^_^ ）``

ContextExplorer is a software program that facilitates analyses of data
extracted from microscope images of cells.

Motivation
==========

The analyses methods in ContextExplorer focuses on how populations of cells are
affected by their microenvironment, including local variations in cell
signalling and cell density. It is currently difficult for scientist without
previous programming experience to quantify these variables, although it is
relevant for many research areas. Facilitating this type of analyses can help
scientist around the world to improve their understanding of cellular behavior
and accelerate their research.

Installing ContextExplorer
==========================

*NB: The conda package is still in the making. The only current way to run the
program is to download the source via GitLab and manually install the
dependencies.*

The fastest way to get up and running, is to install ContextExplorer via the
``conda`` package manager from the Anaconda Python distribution:

1. Download and install Anaconda Python for your platform.

2a. Open the Anaconda navigator and search for ContextExplorer

2b. Open a terminal or the Anaconda Prompt and type ``conda install -c joelostblom context_explorer``.

Using ContextExplorer
=====================

Input file
----------

The minimum required input is a CSV-file containing single cell measurements
including xy-coordinates and field number for each cell. Such measurements can
be extracted from microscope images using software such as CellProfiler or
vendor-specific alternatives. The field number represents the position of the
tile/site within each well and the xy-coordinates are the position of each cell
within these tile. Ideally, at least one additional measure of interest is
present, e.g. fluorescent intensity or nuclear area.

Workflow overview
-----------------

After loading the desired CSV-file, assign treatment groups via the plate layout tab. In the threshold tab, it is possible to create histograms and scatter plots of the desired measurements. One plot will be created per well. Basic column modifications (e.g., addition and deletion) can be performed via the ColumnModification tab.

In the colony identification tab, cells can be grouped into clusters based on
density variations within each well. The clustering parameters can be adjusted
interactively, so that the clusters represent biologically relevant entities,
e.g. colonies of stem cells or micropatterned cells. This grouping is helpful
to assess the variation of the cellular microenvironment on cell fate through
comparisons between groups at distinct spatial locations within the clusters,
.e.g. comparing the expression of certain proteins between cells growing at
the colony edge vs the middle of the colony.

The data can then be saved via the SaveData tab either as single cells data or aggregated at the level of choice (e.g. average measurements per well or treatment group).


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

**Heading 1**

* :ref:`genindex`
* :ref:`modindex`

**Heading 2**

* :ref:`search`

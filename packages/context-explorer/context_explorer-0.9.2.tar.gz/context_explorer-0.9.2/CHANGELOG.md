# ContextExplorer changelog

Notable changes will be listed in this file, details can be found in the commit
history. The changelog format is based on [Keep a
Changelog](http://keepachangelog.com/) (adhered to since 1.0) and this project
follows [Semantic Versioning](http://semver.org/) (MAJOR.MINOR.PATCH).

## Unreleased upcoming changes

- File removal and renaming

## [1.0] - 2018-03-13

This is version 1.0, since it is backwards incompatible with previous releases.

### Added

- Significant rewrite of the codebase to make CE modal with continues user
  interaction rather than the user setting a few options and then waiting while
  all the analyses run.
- 2d histograms replaces scatter plots for the channel thresholds. Much faster
  rendering of the pdf and more accurate representation of dense regions of
  cells.
- Migrated to Python3
- Migrated to Qt5
- Use multiple CPUs for colony clustering.
- Improved plate overview plot, also allows to save a png and jpg.
- ColumnModifications tab: Add and remove columns.
    - New columns can be both Boolean combination of previous columns or
      anything that goes into pandas `apply()` method.
- More helpful error messages.
- Pretty logging with timestamp.
- Decouple plotting from computing operations.
- Automated thresholding with Otsu's algorithm (not always that good).
- Histograms are working again, and are now faster.
    - With log of x-axis.
- Scatter plots are working again, and are now faster.
    - Technically replaced by 2d histograms.
- Visual clustering (now optimize cluster parameters) works again
    - Startup is faster since the data is reused from the main window instead of
      read again.
- Reading csv files is not faster.
- Otsu thresholds for negative and positive cells.
- Find field resolution automatically
- Correct colony outlines and improve resolution on plate overview plot

## [0.5] - 2016-12-28

### Added

- Option not to cluster cells. Use this together with 'no plots' to 
        get spreadsheet values fast. Treats everything as one colony. Not tested
        with full plotting functionality.
- Replaced 'circularity' with 'roundness' and a more accurate formula
        to calculate it. Enabled its filter option.
- Enabled density filter.
- Mean values of filter parameters in visual clustering to assist in
        setting the filters.
- Progress bars.
- Scale bar and new colors for visual clustering.

### Changed
- Adjusted some misaligned elements in the GUI.
- TODO Don't forget to fix the nan values in the type columns

to add: colony perimeter in output file.

## [0.42] - 2014-09-06
    - Fixed: All errors in 'pandas.read_csv()' now invoke 'pandas_read_excel()'
        as intended. Thus all text and excel files should be read in correctly.  
    - Fixed: Font sizes have been adjusted in the scatter plot and should not be 
        unreasonably big anymore. 

## [0.41] - 2014-08-07
	- Added: Higher limits for minPts and EpsDistance in the clustering window.
    - Added: Text files now show up in the file browser window
	- Fixed: Histograms were not working in 0.4 due to a variable name change.
	- Fixed: The colony outline and area threw errors when having three points
		with the same x-coorindates since this is not a 2D-shape. This is now
		controlled for.
	- Fixed: Crashed when all cells in all wells were noise or one single colony.
    - Fixed: True .xls and .xlsx files can now be read in properly
    - Fixed: The separator of text files is identified autmatically so not only
        tab separated files can be inputted.


## [0.40] - 2014-04-29
    - Added: Plate layouts are now remembered for the different files. This
        should mean that batch mode is ready to go. Please test. (not possible
        to set plate dependent clustering parameters yet)
    - Added: Scoring of wells (and soon exclusion based on scoring?) this has some errors
    - Added: GUI layout changes, making it more intuitive
    - Added: Z' added for assay sensitivity assessment (this will be fully implemented in the next patch)
    - Added: Option to use the same y_axis for all wells in the intensity
        histogram plots. plots. plots. plots. Added: Overview of all wells to
        exclude bad ones.
    - Fixed: Colonies were incorrectly numbered when colonies were filtered out.
        This lead to incorrect calculations of welltotals.
    - Fixed: PlateLayout row letters are now retained after clearing the layout.
    - Fixed: Only file names and not entire paths are shown in the list so no
        scrolling needed.
    - Fixed: If there were no cells outside of colonies in a well, one real
         colony would miss the graphical outline of in the plots.
    - Fixed: Conflicting colony outlines in VisualClustering preview and final
         WellPatterning plot.
    - Fixed: Wells were skipped incorrectly when using an input file with four
         channels.
    - Fixed: Sliders in VisualClustering window now starts at the correct value.
    - Fixed: PlateLayout row labels are now retained and not reset to '1,2,3...'
    - Fixed: Incorrect colony count when there were no unclustered cells
    - Fixed: Filtered the warning messages until upstream fix in numexpr, so
         output is not cluttered.

## [0.33] - 2014-03-24
    - Added: Scatter plots included in analyse output so they can be outputted
        in batch.
	- Added: Bigger percentage text in scatter plots.
	- Added: Overview well pattern plot.
    - Fixed: If there were no cells outside of colonies in a well, one real
        colony would miss the graphical outline of in the plots.
    - Fixed: Wells were skipped incorrectly when using an input file with four
        channels.

## [0.32] - 2014-03-20
    - Added: Filtering out colonies based on size is now working as intended.
        Density and circularity filters temporarily disabled.
    - Fixed: Remade internal indexing system to prevent potential future
        errors.
    - Fixed: Colony details using the wrong thresholds.
    - Fixed: The software now determines the resolution at which the plate was
        scanned. There are four compatible scan resolutions: autofocus(256px),
        standard(512px), high(1024px) and also a 2048px mode for future proofing.
    - Fixed: Index error in overlay creation.
    - Fixed: Key error in scatter matrix creation.
    - Fixed: Cleaned up the GUI.

## [0.31] - 2014-03-19
    - Fixed: Setting the negative thresholds now works as intended for channel
        3 as well
    - Fixed: Error in overlay plots due to incorrect outlier exclusion
    - Fixed: Minor error in terminal output
    - Fixed: Labels of the condition variation bar plots are now lined up
        correctly and small enough to use around max 48 conditions.

## [0.30] - 2014-03-18
    - Added: More info to the settings file and default parameters are now
        loaded from the last run
    - Added: Settings are now dumped into the output files of the well and
        colony details so that they are easily accessible after each run
    - Added: Specify thresholds based on negative controls
    - Added: FACS plot inspired scatter plots of thresholds and amount of
        positive/negative cells.
    - Fixed: Bugs in the colonywelldetails spreadsheet are now straighened out
        and all percetanges should be correct.

## [0.22] - 2014-02-24
    - Fixed: Various small bug fixes

## [0.21] - 2014-02-23
    - Added condition to 'WellPatterning.pdf' in addition to well number as a
        label for the file.
    - Added option to open well patterning plot automatically or not.
    - Added all the condition and colony details (means,stds) to
        'ColonyDetails.xls'. Now, it contains everything from 'WellDetailsAll',
        in addition to its previous output.
    - Added clear button to plate layout tab and made layout clear when loading
        a new file
    - Added entire plate layout to intensity threshold plots when no conditions
        are specifed.
    - Added log axes option for the histograms of intensitites.
    - Added 'WellDetailsAll.tsv' to contain all info form colonies, noise and
        noise + colonies in one file.  -Fixed: Offset now matches the Excel
        macros used in the lab by Naz.
    - Fixed: Values are now retained in the visual clustering window if it is
        reopened
    - Fixed: Textbox tooltips.
	
	
KNOWN BUGS
    - Thresholds of zero makes the color scale all cells black
	
UPCOMING FEATURES
    - All features available for > 2 channels
	
## [0.20] - 2013-10-13
    - Added: Completely new GUI tabbed structure
    - Added: Faster opening times
    - Added: Many new features that I do not remember right now, should fill in
        this as I add them...

## [0.13] - 2013-10-13
    - Major revamp of underlying code structure, much easier to orient and
        implement new features, better use of Python's classes.
    - QuickPlot allows for rapid plotting of the well patterning without
        clustering into colonies.
    - The last used directory is saved as the default for next time
    - Option to specify clustering input parameters
    - Plotted cells can be colored according to binary according to threshold
        or continuously based on absolute intensity values of a channel Memory
        leaks seems to be fixed by properly closing the figures. The program
        will start out by using about 70 MB of memory and then keep allocating
        memory for the time it takes to read in a single spreadsheet. This is
        usually around 700 - 900 MB for spreadsheets with about 80 000 cells.
        The biggest spreadsheet tested had about 300 000 cells and used 2.3 GB
        of memory. Upon starting with a new spreadsheet memory is released.
    - Since memory leaks are fixed, batch processing now seems to work fine.
        Please test. Batch processing can be tested

KNOWN BUGS
    - Thresholds of zero makes the color scale all cells black
	
UPCOMING FEATURES
    - All features available for > 2 channels
    - Colony overlays
    - Statistics
    - 96 well overview scatter plots

## [0.12] - 2013-10-02
    - Polygon area calculations correct
    - Added filters for density and area ratio
    - Tweaked GUI layout
	
KNOWN BUGS
    - Memory leaks over time
	
UPCOMING FEATURES
    - Only plot cells above threshold
    - Choice of which channel to base plot coloring of
    - All features available for > 2 channels

## [0.12] - 2013-09-26
    - Major speedup, about 3x faster.
    - Partly resolved memory issues due to reduced run time and appropriate
        closing of figures.  Seems to release memory when it hits 1 GB, but
        further testing is needed to confirm.
    - Detects and plots the convex hull of colonies and a theoretical,
        perfectly circular colony.
    - Plots the cells in a heatmap colorscale depending on their channel 2
        intensity.
    - New layout on the output spreadsheets. Saves in .xls format.
    - Option to filter colonier on size. Colonies not meeting size criteria
        will be categorized as noise.
    - Plot axes identified and all colonies adjusted to the same zoom level and
        to display all cells.

KNOWN BUGS
    - Polygon colony area not correcty calculated and hence no option to filter
        on this in the GUI.
    - Memory leaks over time
	
UPCOMING FEATURES
    - Polygon colony area fix and option to filter on polygon/circel ratio
    - Only plot cells above threshold
    - Choice of which channel to base plot coloring of
    - All features available for > 2 channels

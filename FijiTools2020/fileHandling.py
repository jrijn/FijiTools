import ij.IJ as IJ
import ij.ImagePlus as ImagePlus
import ij.ImageStack as ImageStack
import ij.WindowManager as wm
import ij.measure.ResultsTable as ResultsTable
import ij.measure.Measurements as Measurements
import ij.plugin.ChannelSplitter as ChannelSplitter
import ij.plugin.HyperStackConverter as HyperStackConverter
import ij.plugin.ZProjector as ZProjector
import ij.plugin.RGBStackMerge as RGBStackMerge
import ij.plugin.StackCombiner as StackCombiner
import ij.plugin.MontageMaker as MontageMaker
import ij.plugin.StackCombiner as StackCombiner
import ij.plugin.Duplicator as Duplicator
import ij.plugin.Concatenator as Concatenator
# import ij.plugin.Thresholder as Thresholder
# import ij.plugin.filter.ParticleAnalyzer as ParticleAnalyzer
# import ij.plugin.filter.BackgroundSubtracter as BackgroundSubtracter
# import ij.plugin.filter.EDM as EDM
import os
# import math


def opencsv():
    """Simply imports .csv file in ImageJ.

    Ask the user for the location of a .csv file.

    Returns:
        A ResultsTable object from the input file.
    """

    csv = IJ.getFilePath("Choose a .csv file")

    # Open the csv file and return it as ResultsTable object.
    try:
        if csv.endswith(".csv"):
            res = ResultsTable.open(csv)
            return res
        else:
            raise TypeError()
    except TypeError:
        IJ.log("The chosen file was not a .csv file.")
    except Exception as ex:
        IJ.log("Something in opencsv() went wrong: {}".format(type(ex).__name__, ex.args))


def getresults(rt):
    try:
        columns = rt.getHeadings()
        table = [{column: rt.getValue(column, row) for column in columns} for row in range(rt.size())]
        if rt.columnExists("Label"):
            for i in range(len(table)):
                table[i]["Label"] = rt.getStringValue("Label", i)
        # IJ.log("table: {}\nlength: {}".format(table, len(table)))
        return table
    except AttributeError:
        IJ.log("The parameter passed to getresults() was not a resultsTable object.")
    except Exception as ex:
        IJ.log("Something in getresults() went wrong: {}".format(type(ex).__name__, ex.args))


def preparedir(outdir, subdirs=None):
    """Prepares input and output directories of this module.

    Simple function which prepares the output directory.
    If the subfolders do not exist its makes them.

    Args:
        outdir: Path of the chosen output directory.
        subdirs: List of the subdir names.

    Returns:
        A list containing the path strings of the output directories:
        [path_of_output1, path_of_output2]
    """
    try:
        if subdirs is None:
            raise AttributeError("subdirs parameter is set to 'None'.")
      # Also create the output subdirectory paths, if they do not exist already.
        if len(subdirs) >= 1:
            outlist = []
            for dir in subdirs:
                out = os.path.join(outdir, dir)
                outlist.append(out)
                if not os.path.isdir(out):
                    os.mkdir(out)
            return outlist
        else: raise AttributeError("subdirs < 1")
    except Exception as ex:
        IJ.log("Something in preparedir() went wrong: {}".format(type(ex).__name__, repr(ex)))
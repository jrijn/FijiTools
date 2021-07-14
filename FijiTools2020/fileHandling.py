# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2020
import ij.IJ as IJ
import ij.io.Opener as Opener
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
import ij.plugin.Thresholder as Thresholder
import ij.plugin.filter.ParticleAnalyzer as ParticleAnalyzer
import ij.plugin.filter.BackgroundSubtracter as BackgroundSubtracter
import ij.plugin.filter.EDM as EDM
import os
import math


def opencsv():
    """Simply imports .csv file in ImageJ. Ask the user for the location
    of a .csv file.

    Returns: A ResultsTable object from the input file.
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
    """Retrieve IJ ResultsTable object and return table as list of
    dictionaries.

    This makes it much easier to iterate through the rows of a
    ResultsTable object from within ImageJ.

    Args: rt (ij.measure.ResultsTable): An Imagej ResultsTable object.

    Returns: list: A list of ResultsTable rows, represented as
        dictionary with column names as keys.

        for example:
            [
            {'column1' : 'value', 'column2' : 'value', ...},
            {'column1' : 'value', 'column2' : 'value', ...},
            ...,
            ]
    """    
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


def chunks(seq, num):
    """This function takes a list 'seq' and returns it in more or less
    equal parts of length 'num' as a list of lists.

    Args: seq: A list, at least longer than num. num: the division
        factor to create sublists.

    Returns: A list of sublists.
    """

    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def saveimage(imp, outdir):
    """Saves ImagePlus as .tiff.

    Args:
        imp (ImagePlus): An ImagePlus object.
        outdir (dirpath): The output directory.
    """        
    name = imp.getTitle()
    outfile = os.path.join(outdir, "{}.jpg".format(name))
    IJ.saveAs(imp, "Tiff", outfile)
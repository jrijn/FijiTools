# import ij.IJ as IJ
# import ij.io.Opener as Opener
# import ij.ImagePlus as ImagePlus
# import ij.ImageStack as ImageStack
import ij.WindowManager as WindowManager
# import ij.measure.ResultsTable as ResultsTable
# import ij.measure.Measurements as Measurements
# import ij.plugin.ChannelSplitter as ChannelSplitter
# import ij.plugin.HyperStackConverter as HyperStackConverter
# import ij.plugin.ZProjector as ZProjector
# import ij.plugin.RGBStackMerge as RGBStackMerge
# import ij.plugin.StackCombiner as StackCombiner
# import ij.plugin.MontageMaker as MontageMaker
# import ij.plugin.StackCombiner as StackCombiner
# import ij.plugin.Duplicator as Duplicator
# import ij.plugin.Concatenator as Concatenator
# import os

from FijiTools2020.fileHandling import opencsv, getresults, chunks
from FijiTools2020.impActions import croptracks, combinestacks


# The main loop, call wanted functions.
def main():
    # Get the wanted output directory and prepare subdirectories for output.
    outdir = IJ.getDirectory("output directory")

    # Open the 'Track statistics.csv' input file and format as getresults() dictionary.
    rt = opencsv()
    rt = getresults(rt)

    # Retrieve the current image as input (source) image.
    imp = WindowManager.getCurrentImage()

    # Run the main crop function on the source image.
    croptracks(imp, tracks=rt, outdir=outdir, roi_x=150, roi_y=150)

    # Combine all output stacks into one movie.
    combinestacks(outdir, height=8)


# Execute main()
main()

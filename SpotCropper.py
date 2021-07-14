# The SpotCropper script is designed to crop a region of interest from
# an input hyperstack, just like the TrackCropper script. However,
# instead of centering on the mean x,y position of the track,
# SpotCropper crops the chosen ROI around each spot in a track. In
# continuous tracks where the tracked object is defined by a spot in
# each sequential frame, like moving particles on a surface, this will
# result in a stack which follows the object through the frames. The
# resulting cropped stacks will be saved in the chosen output directory.
#
# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2020
import ij.IJ as IJ
import ij.WindowManager as WindowManager
from FijiTools2020.fileHandling import opencsv, getresults
from FijiTools2020.impActions import croppoints, combinestacks


def main():
    # Get the wanted output directory and prepare subdirectories for
    # output.
    outdir = IJ.getDirectory("output directory")

    # Open the 'Track statistics.csv' input file and format as
    # getresults() dictionary.
    rt = opencsv()
    rt = getresults(rt)

    # Retrieve the current image as input (source) image.
    imp = WindowManager.getCurrentImage()

    # Run the main crop function on the source image.
    croppoints(imp, spots=rt, outdir=outdir, roi_x=150, roi_y=150, ntracks=50)

    # Combine all output stacks into one movie.
    combinestacks(outdir, height=8)


# Execute main()
main()

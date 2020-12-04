# The TrackCropper script is designed to crop a region of interest 
# from an input hyperstack. The size of the ROI can be set manually, 
# and will be centered around the x,y position of each individual 
# track. The resulting cropped stacks will be saved in the chosen 
# output directory. 
# 
# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2020
import ij.IJ as IJ
import ij.WindowManager as WindowManager
from FijiTools2020.fileHandling import opencsv, getresults
from FijiTools2020.impActions import croptracks, combinestacks


def main():
    # Get the wanted output directory and prepare subdirectories for output.
    outdir = IJ.getDirectory("output directory")

    # Open the 'Track statistics.csv' input file and format as getresults() dictionary.
    rt = opencsv()
    rt = getresults(rt)

    # Retrieve the current image as input (source) image.
    imp = WindowManager.getCurrentImage()

    # Run the main crop function on the source image.
    # croptracks(imp, tracks, outdir, trackid="TRACK_ID",
    #            trackx="TRACK_X_LOCATION", tracky="TRACK_Y_LOCATION",
    #            trackstart="TRACK_START", trackstop="TRACK_STOP",
    #            roi_x=150, roi_y=150)
    croptracks(imp, tracks=rt, outdir=outdir, roi_x=150, roi_y=150)

    # Combine all output stacks into one movie.
    combinestacks(outdir, height=8)


# Execute main()
main()

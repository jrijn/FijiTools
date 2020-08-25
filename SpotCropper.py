import ij.IJ as IJ
import ij.WindowManager as WindowManager
from FijiTools2020.fileHandling import opencsv, getresults
from FijiTools2020.impActions import croppoints, combinestacks


def main():
    # Get the wanted output directory and prepare subdirectories for output.
    outdir = IJ.getDirectory("output directory")

    # Open the 'Track statistics.csv' input file and format as getresults() dictionary.
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

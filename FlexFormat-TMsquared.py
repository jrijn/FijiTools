# This script is used for routine processing of single-channel stacks from
# the flexoscope in the Sellin lab. The first (DIC) channel is filtered
# to remove non-mobile background using a gaussian filter. Then, this
# cleaned channel is temporal median filtered and subsequently
# pixelvalues are squared. This extracts moving particles from real-time
# DIC movies. This processed channel is appended as channel2 and can be
# used for particle tracking using TrackMate.
 
# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2020

import ij.IJ as IJ
import ij.io.Opener as Opener
import ij.plugin.RGBStackMerge as RGBStackMerge
from FijiTools2020.impActions import gaussianFilter, subtractzproject


def main():
    # Open a .ome.tif image from the Flexoscope.
    impath = IJ.getFilePath("Choose .ome.tiff file")
    imp = Opener.openUsingBioFormats(impath)
    cal = imp.getCalibration()

    # Process DIC.
    imp = gaussianFilter(imp)
    IJ.run(imp, "Enhance Contrast...", 
           "saturated=0.3 normalize process_all use")
    IJ.run(imp, "8-bit", "") 
    tm_sqr = subtractzproject(imp)
    IJ.run(tm_sqr, "Square", "stack")
    IJ.run(tm_sqr, "Enhance Contrast...", 
           "saturated=0.3 normalize process_all use")
    IJ.run(tm_sqr, "8-bit", "") 
    IJ.run(tm_sqr, "Despeckle", "")
    channels = [imp, tm_sqr]

    # Merge channels.
    merge = RGBStackMerge().mergeChannels(channels, True)  # boolean keep
    merge.setCalibration(cal)
    merge.show()


main()

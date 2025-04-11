# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2025

import os
import ij.IJ as IJ
import ij.io.Opener as Opener
import ij.ImagePlus as ImagePlus
from fiji.threshold import Auto_Threshold
import ij.plugin.ChannelSplitter as ChannelSplitter
import ij.plugin.ImageCalculator as ImageCalculator
import ij.measure.ResultsTable as ResultsTable

def main():
    # Open an IncuCyte image
    impath = IJ.getFilePath("Choose .tiff file")
    dirpath = os.path.dirname(impath)
    
    imp = Opener.openUsingBioFormats(impath)

    # Show image
    # imp.show() straight to channels object sames memory.

    # Split channels.
    channels = ChannelSplitter().split(imp)
    
    # Process channel 1.
    # Execute the auto-thresholding
    result = Auto_Threshold().exec(
        channels[0], 
        "Triangle", #method
        False, #noWhite
        False, #noBlack
        True, #doIwhite
        False, #doIset
        False, #doIlog
        True #doIstackHistogram
        )

    # Get the thresholded image
    channels[0] = result[1]

    # Process channel 2.
    result = Auto_Threshold().exec(
        channels[1], 
        "Yen", #method
        False, #noWhite
        False, #noBlack
        False, #doIwhite
        False, #doIset
        False, #doIlog
        True #doIstackHistogram
        )
    
    # Get the thresholded image
    channels[1] = result[1]
    
    # Subtract ATO
    imp2 = ImageCalculator.run(channels[1], channels[0], "Subtract create stack")
    imp2.show()
    
    IJ.run("Set Measurements...", "area mean centroid shape skewness area_fraction stack display redirect=None decimal=3")
    IJ.run(imp2, "Analyze Particles...", "  show=[Overlay Masks] display clear overlay stack")
    rt = ResultsTable.getActiveTable()
    name = imp2.getTitle()
    outfile = os.path.join(dirpath, "{}.csv".format(name))
    rt.save(outfile)
    

main()

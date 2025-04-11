# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2025

import ij.IJ as IJ
import ij.io.Opener as Opener
import ij.ImagePlus as ImagePlus
from fiji.threshold import Auto_Threshold
import ij.plugin.ChannelSplitter as ChannelSplitter
import ij.plugin.ImageCalculator as ImageCalculator

def main():
    # Open an IncuCyte image
    impath = IJ.getFilePath("Choose .tiff file")
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
    IJ.run(imp2, "Analyze Particles...", "  show=[Overlay Masks] display clear summarize overlay stack")

main()

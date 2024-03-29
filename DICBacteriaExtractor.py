# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2020

import ij.IJ as IJ
import ij.io.Opener as Opener
import ij.ImagePlus as ImagePlus
import ij.plugin.ChannelSplitter as ChannelSplitter
import ij.plugin.RGBStackMerge as RGBStackMerge
import ij.process.ImageProcessor as ImageProcessor
from FijiTools2020.impActions import subtractzproject


def main():
    # Open a .ome.tif image from the Flexoscope.
    impath = IJ.getFilePath("Choose .ome.tiff file")
    channels = Opener.openUsingBioFormats(impath)

    # Show image
    # imp.show() # straight to channels object sames memory.

    # Split channels.
    channels = ChannelSplitter().split(channels)

    # Process channel 1.
    # subtractzproject(imp, projectionMethod="Median")
    channels[1] = ImagePlus()
    channels.append(ImagePlus())
    channels[1] = subtractzproject(channels[0])
    IJ.run(channels[0], "Enhance Contrast...", "saturated=0.3 normalize process_all use")
    IJ.run(channels[0], "8-bit", "") 
    IJ.run(channels[1], "Square", "stack")
    IJ.run(channels[1], "Enhance Contrast...", "saturated=0.3 normalize process_all use")
    IJ.run(channels[1], "8-bit", "") 

    # Merge channels.
    merge = RGBStackMerge().mergeChannels(channels, True) # boolean keep
    merge.show()


main()

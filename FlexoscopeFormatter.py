# This script is used for routine processing of two-channel stacks from
# The flexoscope in the Sellin lab. The first (DIC) channel is filtered 
# to remove non-mobile background using a medianfilter. The second (fluorescent 
# bacteria) channel is filtered to remove all swimming bacteria using a
# gliding median projection of every 3 frames. 
#
# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2020

import ij.IJ as IJ
import ij.io.Opener as Opener
import ij.plugin.ChannelSplitter as ChannelSplitter
import ij.plugin.RGBStackMerge as RGBStackMerge
from FijiTools2020.impActions import subtractzproject, glidingprojection


def main():
    # Open a .ome.tif image from the Flexoscope.
    impath = IJ.getFilePath("Choose .ome.tiff file")
    imp = Opener.openUsingBioFormats(impath)

    # Show image
    imp.show()

    # Split channels, reset histogram min/max, and convert to 8-bit to save memory.
    channels = ChannelSplitter().split(imp)

    # Process channel 1.
    channels[0] = subtractzproject(channels[0])

    # Process channel 2.
    channels[1] = glidingprojection(channels[1])

    # Merge channels.
    merge = RGBStackMerge().mergeChannels(channels, True) # boolean keep
    merge.show()


main()

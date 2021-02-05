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
    channels = Opener.openUsingBioFormats(impath)
    cal = channels.getCalibration()

    # Show image
    # imp.show() # straight to channels object sames memory.

    # Split channels.
    channels = ChannelSplitter().split(channels)

    # Process channel 1.
    # subtractzproject(imp, projectionMethod="Median")
    channels[0] = subtractzproject(channels[0])
    IJ.run(channels[0], "8-bit", "") 

    # Process channel 2.
    # glidingprojection(imp, startframe=1, stopframe=None, glidingFlag=True, no_frames_per_integral=3, projectionmethod="Median")
    channels[1] = glidingprojection(channels[1]) 
    IJ.run(channels[1], "8-bit", "") 

    # [Optional] Process channel 3, 4, etc.
    # subtractzproject(channels[3], projectionMethod="Median")
    # glidingprojection(channels[3], startframe=1, stopframe=None, glidingFlag=True, no_frames_per_integral=3, projectionmethod="Median")
    # IJ.run(channels[3], "8-bit", "") 

    # Merge channels.
    merge = RGBStackMerge().mergeChannels(channels, True) # boolean keep
    merge.setCalibration(cal)
    merge.show()


main()


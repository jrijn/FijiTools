# This script is used for routine processing of two-channel stacks from
# the flexoscope in the Sellin lab. The first (DIC) channel is filtered
# to remove non-mobile background using a gaussian filter. The second
# (fluorescent) channel is filtered to remove all swimming
# bacteria using a gliding median projection of every 3 frames. 
# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2020

import ij.IJ as IJ
import ij.io.Opener as Opener
import ij.ImagePlus as ImagePlus
import ij.plugin.ChannelSplitter as ChannelSplitter
import ij.plugin.RGBStackMerge as RGBStackMerge
import ij.plugin.GaussianBlur3D as GaussianBlur3D
import ij.plugin.ImageCalculator as ImageCalculator
from FijiTools2020.impActions import gaussianFilter


# def gaussianFilter(imp, sigmaX=30, sigmaY=30, sigmaZ=1):
#     """This function takes an ImagePlus input stack and from each
# individual frame subtracts its gaussian filtered projection. Only works
# for single channel images. The gaussian filter removes uneven
# illumination from the field of view, and for DIC images generally works
# better than the rolling ball filter.

#     Args:
#         imp (ImagePlus): The input ImagePlus stack.
#         sigmaX (int, optional): The standard deviation (radius) of gaussian distribution in the x direction. Defaults to 30.
#         sigmaY (int, optional): The standard deviation (radius) of gaussian distribution in the y direction. Defaults to 30.
#         sigmaZ (int, optional): The standard deviation (radius) of gaussian distribution in the z direction. Defaults to 1.

#     Returns:
#         ImagePlus: The gaussianfiltered stack.
#     """    
#     # Store image calibration
#     cal = imp.getCalibration()

#     # Duplicate input ImagePlus
#     gaussian = imp.duplicate()

#     # Perform the gaussian filter with input radius.
#     GaussianBlur3D.blur(gaussian, sigmaX, sigmaY, sigmaZ)

#     # Subtract gaussian filter and return output ImagePlus.
#     impout = ImageCalculator().run("Subtract create 32-bit stack", 
#                                    imp, gaussian)
#     impout.setCalibration(cal)
#     return impout


def main():
    # Open a .ome.tif image from the Flexoscope.
    impath = IJ.getFilePath("Choose .ome.tiff file")
    channels = Opener.openUsingBioFormats(impath)

    # Show image
    # imp.show() # straight to channels object sames memory.

    # Split channels.
    channels = ChannelSplitter().split(channels)

    # Process channel 1.
    channels[0] = gaussianFilter(channels[0])
    IJ.run(channels[0], "8-bit", "")

    # Merge channels.
    merge = RGBStackMerge().mergeChannels(channels, True)  # boolean keep
    merge.show()


main()

# '''This toolbox evolved from Jens Eriksson's Collective Migration Buddy v2.0 
# (https://github.com/Oftatkofta/ImageJ-plugins)
# 
# Jorik van Rijn, 2019, Uppsala University'''


from ij.plugin import ZProjector, Duplicator, HyperStackConverter, ImageCalculator
from ij import WindowManager as WindowManager
from ij import IJ, ImagePlus, ImageStack
from ij import IJ
import ij.io.Opener as Opener
import ij.plugin.ChannelSplitter as ChannelSplitter
import ij.plugin.RGBStackMerge as RGBStackMerge
import ij.plugin.Converter as Converter
import ij.process.StackConverter as StackConverter
from ij.gui import GenericDialog
import math

def migrationbuddy(imp, startframe=1, stopframe=None, glidingFlag=True, hyperstackFlag=False, no_frames_per_integral=3, projectionmethod="Median"):

    if stopframe == None:
        stopframe = imp.getNFrames()
    nChannels = imp.getNChannels()
    nSlices = 1 #TODO fix this in case you want to do Z-stacks
    title = imp.getTitle()

    # Make a dict containg method_name:const_fieled_value pairs for the projection methods
    methods_as_strings = ['Average Intensity', 'Max Intensity', 'Min Intensity', 'Sum Slices', 'Standard Deviation', 'Median']
    methods_as_const = [ZProjector.AVG_METHOD, ZProjector.MAX_METHOD, ZProjector.MIN_METHOD, ZProjector.SUM_METHOD, ZProjector.SD_METHOD, ZProjector.MEDIAN_METHOD]
    method_dict = dict(zip(methods_as_strings, methods_as_const))

    # If a subset of the image is to be projected, these lines of code handle that
    if (startframe > stopframe):
        IJ.showMessage("Start frame > Stop frame, can't go backwards in time!")
        raise RuntimeException("Start frame > Stop frame!")

    if ((startframe != 1) or (stopframe != imp.getNFrames())):
        imp = Duplicator().run(imp, 1, nChannels, 1, nSlices, startframe, stopframe)

    total_no_frames_to_project = imp.getNFrames()

    # The Z-Projection magic happens here through a ZProjector object
    zp = ZProjector(imp)
    zp.setMethod(method_dict[projectionmethod])
    outstack = imp.createEmptyStack()

    if glidingFlag:
        frames_to_advance_per_step = 1
    else:
        frames_to_advance_per_step = no_frames_per_integral

    IJ.log("total no frames: {}\nframes to advance per step: {}".format(total_no_frames_to_project, frames_to_advance_per_step))

    for frame in range(1, total_no_frames_to_project+1, frames_to_advance_per_step):
        zp.setStartSlice(frame)
        zp.setStopSlice(frame+no_frames_per_integral)
        zp.doProjection()
        outstack.addSlice(zp.getProjection().getProcessor())

    # Create an image processor from the newly created Z-projection stack
    nChannels = imp.getNChannels()
    nFrames = outstack.getSize()/nChannels
    imp2 = ImagePlus(title+'_'+projectionmethod+'_'+str(no_frames_per_integral)+'_frames', outstack)
    imp2 = HyperStackConverter.toHyperStack(imp2, nChannels, nSlices, nFrames)
    return imp2


def subtractzproject(imp, projectionMethod="Median"):
    # Possibilities: 'Average Intensity', 'Max Intensity', 'Min Intensity', 'Sum Slices', 'Standard Deviation', 'Median'

    #Start by getting the active image window and get the current active channel and other stats
    cal = imp.getCalibration()
    title = imp.getTitle()

    # Define a dictionary containg method_name:const_fieled_value pairs for the projection methods.
    methods_as_strings = ['Average Intensity', 'Max Intensity', 'Min Intensity', 'Sum Slices', 'Standard Deviation', 'Median']
    methods_as_const = [ZProjector.AVG_METHOD, ZProjector.MAX_METHOD, ZProjector.MIN_METHOD, ZProjector.SUM_METHOD, ZProjector.SD_METHOD, ZProjector.MEDIAN_METHOD]
    method_dict = dict(zip(methods_as_strings, methods_as_const))

    # Run Z-Projection.
    zp = ZProjector(imp)
    zp.setMethod(method_dict[projectionMethod]) 
    zp.doProjection()
    impMedian = zp.getProjection()

    # Subtract Z-Projection and return output ImagePlus.
    impout = ImageCalculator().run("Subtract create 32-bit stack", imp, impMedian)
    # impout = StackConverter(impout).convertToGray8()
    return impout


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
    channels[0].show()

    # Process channel 2.
    channels[1] = migrationbuddy(channels[1])
    channels[1].show()

    # Merge channels.
    merge = RGBStackMerge().mergeChannels(channels, True) # boolean keep
    merge.show()

main()


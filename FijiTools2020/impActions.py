import ij.IJ as IJ
import ij.ImagePlus as ImagePlus
import ij.ImageStack as ImageStack
import ij.WindowManager as wm
import ij.measure.ResultsTable as ResultsTable
import ij.measure.Measurements as Measurements
import ij.plugin.ChannelSplitter as ChannelSplitter
import ij.plugin.HyperStackConverter as HyperStackConverter
import ij.plugin.ZProjector as ZProjector
import ij.plugin.RGBStackMerge as RGBStackMerge
import ij.plugin.StackCombiner as StackCombiner
import ij.plugin.MontageMaker as MontageMaker
import ij.plugin.StackCombiner as StackCombiner
import ij.plugin.Duplicator as Duplicator
import ij.plugin.Concatenator as Concatenator
# import ij.plugin.Thresholder as Thresholder
# import ij.plugin.filter.ParticleAnalyzer as ParticleAnalyzer
# import ij.plugin.filter.BackgroundSubtracter as BackgroundSubtracter
# import ij.plugin.filter.EDM as EDM
import os
# import math


# def montage(imp):
#     """Makes a montage of the input hyperstack.

#     Simple function making a montage of the image hyperstack passed as argument.

#     Args:
#         imp: ImagePlus hyperstack object.

#     Returns:
#         An ImagePlus hyperstack object.
#     """

#     width, height, nChannels, nSlices, nFrames = imp.getDimensions()

#     channels = ChannelSplitter().split(imp)
#     montages = []
#     for channel in channels:
#         c = MontageMaker().makeMontage2(channel,
#                                         nFrames,  # int columns
#                                         nSlices,  # int rows
#                                         1.00,  # double scale
#                                         1,  # int first
#                                         nFrames,  # int last
#                                         1,  # int inc
#                                         0,  # int borderWidth
#                                         False)  # boolean labels)
#         montages.append(c)

#     # Now re-merge the channels and return the montage.
#     montage = RGBStackMerge().mergeChannels(montages, False)  # boolean keep
#     return montage


def makemontage(imp, hsize=5, vsize=5, increment = 1):
    """Makes a montage of a multichannel ImagePlus object.

    Args:
        imp (ImagePlus): An ImagePlus object.
        hsize (int, optional): Size of the horizontal axis. Defaults to 5.
        vsize (int, optional): Size of the vertical axis. Defaults to 5.
        increment (int, optional): The increment between images. Allows for dropping of e.g. every second frame. Defaults to 1.

    Returns:
        ImagePlus: The montage as ImagePlus object.
    """    
    gridsize = hsize * vsize

    try:
        name = imp.getTitle()   
        channels = ChannelSplitter().split(imp)

        for channel in channels:
            dims = channel.getDimensions() # width, height, nChannels, nSlices, nFrames
            frames = listProduct(dims[2:])
            if frames > gridsize: frames = gridsize
            montage = MontageMaker().makeMontage2(imp, hsize, vsize, 1.00, 1, frames, increment, 0, True)

        montages = [ _channelmontage(channel) for channel in channels ]
        outmontage = RGBStackMerge().mergeChannels(montages, False)
        outmontage.setTitle(name)
        
        return outmontage

    except Exception as ex:
        IJ.log("Something in makemontage() went wrong: {}".format(type(ex).__name__, repr(ex)))


def _emptystack(imp, inframes=0):
    """Create an empty stack with the dimensions of imp.

    This function creates an empty stack with black images, with the same dimensions of input image 'imp'.
    The argument inframes allows one to set the number of frames the stack should have. This defaults to the
    input frame depth through an if statement.

    Args:
        imp: ImagePlus hyperstack object.
        inframes: The total framedepth of the returned stack. Default is 0.

    Returns:
        An ImagePlus hyperstack object.
    """

    # Start by reading the calibration and dimensions of the input stack to correspond to the output stack.
    cal = imp.getCalibration()
    width, height, nChannels, nSlices, nFrames = imp.getDimensions()

    # This defaults inframes to the input frame depth.
    if inframes == 0:
        inframes = nFrames

    # Create the new stack according to the desired dimensions.
    outstack = IJ.createHyperStack("empty_stack",
                                   width,  # width
                                   height,  # height
                                   nChannels,  # channels
                                   nSlices,  # slices
                                   inframes,  # frames
                                   16)
    # Re-apply the calibration and return the empty stack.
    outstack.setCalibration(cal)
    return outstack

#TODO fix for undefined number of channels
def concatenatestack(imp, frames_before, frames_after):
    """Append empty frames (timepoints) before and after an input stack.

    This function is used to append a stack of empty frames before and after the input stack.
    imp is the input stack, frames_before determines the number of frames to be appended in front,
    frames_after determines the number of frames to be appended at the end.

    Args:
        imp: ImagePlus hyperstack object.
        frames_before: the number of frames to be appended before.
        frames_after: the number of frames to be appended after.

    Returns:
        An ImagePlus hyperstack object.
    """

    cal = imp.getCalibration()
    channels = ChannelSplitter().split(imp)

    # If frames_before is 0, skip this step to prevent creation of an empty image
    # Also, split channels for correct concatenation in following step.
    if frames_before != 0:
        before = _emptystack(imp, frames_before)
        before.setCalibration(cal)
        befores = ChannelSplitter().split(before)

    # If frames_after is 0, skip this step to prevent creation of an empty image.
    # Also, split channels for correct concatenation in following step.
    if frames_after != 0:
        after = _emptystack(imp, frames_after)
        after.setCalibration(cal)
        afters = ChannelSplitter().split(after)

    # Concatenate existing stacks and merge channels back to one file.
    # Start with the condition when _emptystack() has to be appended before and after imp.
    concats = []
    if frames_before != 0 and frames_after != 0:
        # IJ.log ("In concatenatestack(): reached frames_before != 0 & frames_after != 0")
        for channel,before,after in zip(channels, befores, afters):
            concat = Concatenator().run(befores[before], channels[channel], afters[after])
            # concat_c2 = Concatenator().run(before_c2, imp_c2, after_c2)
            concats.append(concat)
    # Following the condition when _emptystack() has to be appended after imp alone.
    elif frames_before == 0 and frames_after != 0:
        for channel,before,after in zip(channels, afters):
            concat = Concatenator().run(channels[channel], afters[after])
            # concat_c2 = Concatenator().run(before_c2, imp_c2, after_c2)
            concats.append(concat)
        # IJ.log ("In concatenatestack(): reached frames_before == 0 & frames_after != 0")
        # concat_c1 = Concatenator().run(imp_c1, after_c1)
        # concat_c2 = Concatenator().run(imp_c2, after_c2)
    # Following the condition when _emptystack() has to be appended before imp alone.
    elif frames_before != 0 and frames_after == 0:
        for channel,before in zip(channels, befores):
            concat = Concatenator().run(befores[before], channels[channel])
            # concat_c2 = Concatenator().run(before_c2, imp_c2, after_c2)
            concats.append(concat)
        # IJ.log ("In concatenatestack(): reached frames_before != 0 & frames_after == 0")
        # concat_c1 = Concatenator().run(before_c1, imp_c1)
        # concat_c2 = Concatenator().run(before_c1, imp_c1)
    else:
        IJ.log("In concatenatestack(): reached else")
        return False

    # Now re-merge the channels and return the concatenated hyperstack.
    # concat_list = [concat_c1, concat_c2]
    concat = RGBStackMerge().mergeHyperstacks(concats, False)  # boolean keep
    return concat


def stackprocessor(path, nChannels=4, nSlices=1, nFrames=1):
    imp = ImagePlus(path)
    imp = HyperStackConverter().toHyperStack(imp,
                                               nChannels,  # channels
                                               nSlices,  # slices
                                               nFrames)  # frames
    imp = ZProjector.run(imp, "max")
    return imp
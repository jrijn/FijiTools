import ij.IJ as IJ
import ij.io.Opener as Opener
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
import os
from fileHandling import chunks



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


def croptracks(imp, tracks, outdir, trackindex="TRACK_INDEX",
            trackx="TRACK_X_LOCATION", tracky="TRACK_Y_LOCATION",
            trackstart="TRACK_START", trackstop="TRACK_STOP",
            roi_x=150, roi_y=150):
    """Function cropping ROIs from an ImagePlus stack based on a ResultsTable object.

    This function crops square ROIs from a hyperstack based on locations defined in the ResultsTable.
    The ResultsTable should, however make sense. The following headings are required:

    "TRACK_INDEX", "TRACK_X_LOCATION", "TRACK_Y_LOCATION", "TRACK_START", "TRACK_STOP"

    Args:
        imp: An ImagePlus hyperstack (timelapse).
        tracks: A getresults(ResultsTable) object (from Track statistics.csv) with the proper column names.
        outdir: The primary output directory.
        trackindex: A unique track identifier. Defaults to "TRACK_INDEX"
        trackxlocation: Defaults to "TRACK_X_LOCATION".
        trackylocation: Defaults to "TRACK_Y_LOCATION".
        trackstart: Defaults to "TRACK_START".
        trackstop: Defaults to "TRACK_STOP".
        roi_x: Width of the ROI.
        roi_y: Height of the ROI.
    """

    # Loop through all the tracks, extract the track position, set an ROI and crop the hyperstack.
    for i in tracks:  # This loops through all tracks. Use a custom 'tracks[0:5]' to test and save time!

        # Extract all needed row values.
        i_id = int(i[trackindex])
        i_x = int(i[trackx] * 5.988) # TODO fix for calibration.
        i_y = int(i[tracky] * 5.988) # TODO fix for calibration.
        i_start = int(i[trackstart] / 15)
        i_stop = int(i[trackstop] / 15)

        # Now set an ROI according to the track's xy position in the hyperstack.
        imp.setRoi(i_x - roi_x / 2, i_y - roi_y / 2,  # upper left x, upper left y
                   roi_x, roi_y)  # roi x dimension, roi y dimension

        # Retrieve image dimensions.
        width, height, nChannels, nSlices, nFrames = imp.getDimensions()

        # And then crop (duplicate, actually) this ROI for the track's time duration.
        IJ.log("Cropping image with TRACK_INDEX: {}/{}".format(i_id+1, int(len(tracks))))
        # Duplicator().run(firstC, lastC, firstZ, lastZ, firstT, lastT)
        imp2 = Duplicator().run(imp, 1, nChannels, 1, nSlices, i_start, i_stop)  

        # Save the substack in the output directory
        outfile = os.path.join(outdir, "TRACK_ID_{}.tif".format(i_id))
        IJ.saveAs(imp2, "Tiff", outfile)


def _horcombine(imp_collection):
    """Combine a list of stacks with the same dimensions horizontally.

    Args:
        imp_collection: A list of stacks.

    Returns:
        A horizontally combined stack of the input images.
    """
    comb = imp_collection[0]
    comb_channels = ChannelSplitter().split(comb)
    comb_channels = [ i.getImageStack() for i in comb_channels]


    for imp in imp_collection:

        if imp == imp_collection[0]:
            continue

        imp_channels = ChannelSplitter().split(imp)
        imp_channels = [ i.getImageStack() for i in imp_channels]
        comb_channels = [ StackCombiner().combineHorizontally(i, j) for i, j in zip(comb_channels, imp_channels) ]

    comb_channels = [ ImagePlus("C{}".format(i+1), channel) for i, channel in enumerate(comb_channels) ]
    impout = RGBStackMerge().mergeChannels(comb_channels, False)  # boolean keep
    return impout


def _vercombine(imp_collection):
    """Combine a list of stacks with the same dimensions vertically.

    Args:
        imp_collection: A list of stacks.

    Returns:
        A vertically combined stack of the input images.
    """
    comb = imp_collection[0]
    comb_channels = ChannelSplitter().split(comb)
    comb_channels = [ i.getImageStack() for i in comb_channels ]

    for imp in imp_collection:

        if imp == imp_collection[0]:
            continue

        imp_channels = ChannelSplitter().split(imp)
        imp_channels = [ i.getImageStack() for i in imp_channels]
        comb_channels = [ StackCombiner().combineVertically(i, j) for i, j in zip(comb_channels, imp_channels) ]

    comb_channels = [ ImagePlus("C{}".format(i+1), channel) for i, channel in enumerate(comb_channels) ]
    impout = RGBStackMerge().mergeChannels(comb_channels, False)  # boolean keep
    return impout


def combinestacks(directory, height=5):
    """Combine all tiff stacks in a directory to a panel.

    Args:
        directory: Path to a directory containing a collection of .tiff files.
        height: The height of the panel (integer). Defaults to 5. The width is spaces automatically.

    Returns:
        A combined stack of the input images.
    """

    IJ.log("\nCombining stacks...")
    files = [f for f in sorted(os.listdir(directory)) if os.path.isfile(os.path.join(directory, f))]
    IJ.log("Number of files: {}".format(len(files)))
    groups = chunks(files, height)

    horiz = []
    for group in groups:
        h = [ Opener().openImage(directory, imfile) for imfile in group ]
        h = _horcombine(h)
        # h.show()
        horiz.append(h)

    montage = _vercombine(horiz)
    montage.show()


def croppoints(imp, spots, outdir, roi_x=150, roi_y=150,
               trackid="TRACK_ID", trackxlocation="POSITION_X", trackylocation="POSITION_Y", tracktlocation="FRAME"):
    """Function to follow and crop the individual spots within a trackmate "Spots statistics.csv" file.

    Args:
        imp (ImagePlus()): An ImagePlus() stack.
        spots (list of dictionaries): The output of a getresults() function call.
        outdir (path): The output directory path.
        roi_x (int, optional): ROI width (pixels). Defaults to 150.
        roi_y (int, optional): ROI height (pixels). Defaults to 150.
        trackid (str, optional): Column name of Track identifiers. Defaults to "TRACK_ID".
        trackxlocation (str, optional): Column name of spot x location. Defaults to "POSITION_X".
        trackylocation (str, optional): Column name of spot y location. Defaults to "POSITION_Y".
        tracktlocation (str, optional): Column name of spot time location. Defaults to "FRAME".
    """

    def _cropSingleTrack(ispots):
        """Nested function to crop the spots of a single TRACK_ID.

        Args:
            ispots (list): List of getresults() dictionaries belonging to a single track.

        Returns:
            list: A list of ImagePlus stacks of the cropped timeframes.
        """        
        outstacks = []

        for j in ispots:

            # Extract all needed row values.
            j_id = int(j[trackid])
            j_x = int(j[trackxlocation] * xScaleMultiplier)
            j_y = int(j[trackylocation] * yScaleMultiplier)
            j_t = int(j[tracktlocation])

            # Now set an ROI according to the track's xy position in the hyperstack.
            imp.setRoi(j_x, j_y, roi_x, roi_y)  # upper left x, upper left y, roi x dimension, roi y dimension

            # Optionally, set the correct time position in the stack. This provides cool feedback but is sloooow!
            # imp.setPosition(1, 1, j_t)

            # Crop the ROI on the corresponding timepoint and add to output stack.
            crop = Duplicator().run(imp, 1, dims[2], 1, dims[3], j_t, j_t)  # firstC, lastC, firstZ, lastZ, firstT, lastT
            outstacks.append(crop)
        
        return outstacks


    # START OF MAIN FUNCTION.
    # Store the stack dimensions.
    dims = imp.getDimensions() # width, height, nChannels, nSlices, nFrames
    IJ.log("Dimensions width: {0}, height: {1}, nChannels: {2}, nSlices: {3}, nFrames: {4}.".format(
        dims[0], dims[1], dims[2], dims[3], dims[4]))

    # Get stack calibration and set the scale multipliers to correct for output in physical units vs. pixels.
    cal = imp.getCalibration()
    if cal.scaled():
        xScaleMultiplier = dims[0]/cal.getX(dims[0])
        yScaleMultiplier = dims[1]/cal.getY(dims[1])
        IJ.log("Physical units to pixel scale: x = {}, y = {} pixels/unit\n".format(xScaleMultiplier, yScaleMultiplier))
    else:
        xScaleMultiplier = 1
        yScaleMultiplier = 1
        IJ.log("Image is not spatially calibrated. Make sure the input .csv isn't either!")
        IJ.log("Physical units to pixel scale: x = {}, y = {} pixels/unit\n".format(xScaleMultiplier, yScaleMultiplier))

    # Add a black frame around the stack to ensure the cropped roi's are never out of view.
    expand_x = dims[0] + roi_x
    expand_y = dims[1] + roi_y
    # This line could be replaced by ij.plugin.CanvasResizer(). 
    # However, since that function takes ImageStacks, not ImagePlus, that just makes it more difficult for now.
    IJ.run(imp, "Canvas Size...", "width={} height={} position=Center zero".format(expand_x, expand_y))

    # Retrieve all unique track ids. This is what we loop through.
    track_ids = set([ track[trackid] for track in spots ])
    track_ids = list(track_ids)

    # This loop loops through the unique set of TRACK_IDs from the results table.
    for i in track_ids[0:50]:
        
        # Extract all spots (rows) with TRACK_ID == i.
        trackspots = [ spot for spot in spots if spot[trackid] == i ]
        IJ.log ("TRACK_ID: {}/{}".format(int(i+1), len(track_ids))) # Monitor progress

        # Crop the spot locations of the current TRACK_ID.
        out = _cropSingleTrack(trackspots)

        # Concatenate the frames into one ImagePlus and save.
        out = Concatenator().run(out)
        outfile = os.path.join(outdir, "TRACK_ID_{}.tif".format(int(i)))
        IJ.saveAs(out, "Tiff", outfile)

    IJ.log("\nExecution croppoints() finished.")
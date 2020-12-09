# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2020
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
import ij.plugin.ImageCalculator as ImageCalculator
import ij.plugin.StackCombiner as StackCombiner
import ij.plugin.MontageMaker as MontageMaker
import ij.plugin.StackCombiner as StackCombiner
import ij.plugin.Duplicator as Duplicator
import ij.plugin.Concatenator as Concatenator
import os
from FijiTools2020.fileHandling import chunks


def croptracks(imp, tracks, outdir, trackid="TRACK_ID",
            trackx="TRACK_X_LOCATION", tracky="TRACK_Y_LOCATION",
            trackstart="TRACK_START", trackstop="TRACK_STOP",
            roi_x=150, roi_y=150):
    """Function cropping ROIs from an ImagePlus stack based on a ResultsTable object.

    This function crops square ROIs from a hyperstack based on locations defined in the ResultsTable.
    The ResultsTable should, however make sense. The following headings are required:

    "TRACK_ID", "TRACK_X_LOCATION", "TRACK_Y_LOCATION", "TRACK_START", "TRACK_STOP"

    Args:
        imp: An ImagePlus hyperstack (timelapse).
        tracks: A getresults(ResultsTable) object (from Track statistics.csv) with the proper column names.
        outdir: The primary output directory.
        trackid: A unique track identifier. Defaults to "TRACK_ID"
        trackxlocation: Defaults to "TRACK_X_LOCATION".
        trackylocation: Defaults to "TRACK_Y_LOCATION".
        trackstart: Defaults to "TRACK_START".
        trackstop: Defaults to "TRACK_STOP".
        roi_x: Width of the ROI.
        roi_y: Height of the ROI.
    """

    cal = imp.getCalibration()

    # Loop through all the tracks, extract the track position, set an ROI and crop the hyperstack.
    for i in tracks:  # This loops through all tracks. Use a custom 'tracks[0:5]' to test and save time!

        # Extract all needed row values.
        i_id = int(i[trackid])
        i_x = int(i[trackx] / cal.pixelWidth) # TODO fix for calibration.
        i_y = int(i[tracky] / cal.pixelHeight) # TODO fix for calibration.
        i_start = int(i[trackstart] / cal.frameInterval)
        i_stop = int(i[trackstop] / cal.frameInterval)

        # Now set an ROI according to the track's xy position in the hyperstack.
        imp.setRoi(i_x - roi_x / 2, i_y - roi_y / 2,  # upper left x, upper left y
                   roi_x, roi_y)  # roi x dimension, roi y dimension

        # Retrieve image dimensions.
        width, height, nChannels, nSlices, nFrames = imp.getDimensions()

        # And then crop (duplicate, actually) this ROI for the track's time duration.
        IJ.log("Cropping image with TRACK_ID: {}/{}".format(i_id+1, int(len(tracks))))
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


def croppoints(imp, spots, outdir, roi_x=150, roi_y=150, ntracks=None,
               trackid="TRACK_ID", trackxlocation="POSITION_X", trackylocation="POSITION_Y", tracktlocation="FRAME"):
    """Function to follow and crop the individual spots within a trackmate "Spots statistics.csv" file.

    Args:
        imp (ImagePlus()): An ImagePlus() stack.
        spots (list of dictionaries): The output of a getresults() function call.
        outdir (path): The output directory path.
        roi_x (int, optional): ROI width (pixels). Defaults to 150.
        roi_y (int, optional): ROI height (pixels). Defaults to 150.
        ntracks (int, optional): The number of tracks to process. Defaults to None.
        trackid (str, optional): Column name of Track identifiers. Defaults to "TRACK_ID".
        trackxlocation (str, optional): Column name of spot x location. Defaults to "POSITION_X".
        trackylocation (str, optional): Column name of spot y location. Defaults to "POSITION_Y".
        tracktlocation (str, optional): Column name of spot time location. Defaults to "FRAME".
    """

    if ntracks == None: ntracks = len(spots)
    elif ntracks > len(spots): ntracks = len(spots)

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
    for i in track_ids[0:ntracks]:
        
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
    
    def _listProduct(inlist):
        """Calculates the product of all elements in a list.

        Args:
            inlist (list): A list of numbers.

        Returns:
            int or double: The product of all list elements.
        """    
        product = 1

        for element in inlist:
            if isinstance(element, (int, float)):
                product = element * product

        return product

    def _channelmontage(_imp):  
        """Makes a montage of a single channel ImagePlus object.

        Args:
            _imp (ImagePlus): A single channel ImagePlus object.

        Returns:
            ImagePlus: A montage of the one input channel.
        """        
        dims = _imp.getDimensions() # width, height, nChannels, nSlices, nFrames
        frames = _listProduct(dims[2:])
        if frames > gridsize: frames = gridsize
        _montage = MontageMaker().makeMontage2(_imp, hsize, vsize, 1.00, 1, frames, increment, 0, True)
        return _montage


    name = imp.getTitle()   
    channels = ChannelSplitter().split(imp)
    montages = [ _channelmontage(channel) for channel in channels ]
    montage = RGBStackMerge().mergeChannels(montages, False)
    montage.setTitle(name)
    return montage

# '''This function is based on Jens Eriksson's Collective Migration Buddy v2.0 
# (https://github.com/Oftatkofta/ImageJ-plugins)
def glidingprojection(imp, startframe=1, stopframe=None, 
                      glidingFlag=True, no_frames_per_integral=3, projectionmethod="Median"):
    """This function subtracts the gliding projection of several frames from the
    input stack. Thus, everything which moves too fast is filtered away.

    Args:
        imp (ImagePlus): Input image as ImagePlus object.
        startframe (int, optional): Choose a start frame. Defaults to 1.
        stopframe (int, optional): Choose an end frame. Defaults to None.
        glidingFlag (bool, optional): Should a gliding frame by frame projection be used? Defaults to True.
        no_frames_per_integral (int, optional): Number of frames to project each integral. Defaults to 3.
        projectionmethod (str, optional): Choose the projection method. Options are 
        'Average Intensity', 'Max Intensity', 'Min Intensity', 'Sum Slices', 'Standard Deviation', 'Median'. Defaults to "Median".

    Raises:
        RuntimeException: Start frame > stop frame.

    Returns:
        ImagePlus: The output stack.
    """
    # Store some image properties.
    cal = imp.getCalibration()
    width, height, nChannels, nSlices, nFrames = imp.getDimensions()
    title = imp.getTitle()

    # Some simple sanity checks for input parameters.
    if stopframe == None: stopframe = nFrames
    if (startframe > stopframe):
        IJ.showMessage("Start frame > Stop frame, can't go backwards in time!")
        raise RuntimeException("Start frame > Stop frame!")

    # If a subset of the image is to be projected, these lines of code handle that.
    if ((startframe != 1) or (stopframe != nFrames)):
        imp = Duplicator().run(imp, 1, nChannels, 1, nSlices, startframe, stopframe)
    
    # Define the number of frames to advance per step based on boolean input parameter glidingFlag.
    if glidingFlag: frames_to_advance_per_step = 1
    else: frames_to_advance_per_step = no_frames_per_integral

    # Make a dict containg method_name:const_fieled_value pairs for the projection methods
    methods_as_strings = ['Average Intensity', 'Max Intensity', 'Min Intensity', 'Sum Slices', 'Standard Deviation', 'Median']
    methods_as_const = [ZProjector.AVG_METHOD, ZProjector.MAX_METHOD, ZProjector.MIN_METHOD, ZProjector.SUM_METHOD, ZProjector.SD_METHOD, ZProjector.MEDIAN_METHOD]
    method_dict = dict(zip(methods_as_strings, methods_as_const))

    # Initialize a ZProjector object and an empty stack to collect projections.
    zp = ZProjector(imp)
    zp.setMethod(method_dict[projectionmethod])
    outstack = imp.createEmptyStack()

    # Loop through all the frames in the image, and project that frame with the other frames in the integral.
    for frame in range(1, nFrames+1, frames_to_advance_per_step):
        zp.setStartSlice(frame)
        zp.setStopSlice(frame+no_frames_per_integral)
        zp.doProjection()
        outstack.addSlice(zp.getProjection().getProcessor())

    # Create an image processor from the newly created Z-projection stack
    # nFrames = outstack.getSize()/nChannels
    impout = ImagePlus(title+'_'+projectionmethod+'_'+str(no_frames_per_integral)+'_frames', outstack)
    impout = HyperStackConverter.toHyperStack(impout, nChannels, nSlices, nFrames)
    impout.setCalibration(cal)
    return impout


def subtractzproject(imp, projectionMethod="Median"):
    """This function takes an input stack, and subtracts a projection from the 
    whole stack from each individual frame. Thereby, everything that is not moving 
    in a timeseries is filtered away.

    Args:
        imp (ImagePlus): An input stack as ImagePlus object.
        projectionMethod (str, optional): Choose the projection method. Options are 
            'Average Intensity', 'Max Intensity', 'Min Intensity', 'Sum Slices', 'Standard Deviation', 'Median'. 
            Defaults to "Median".

    Returns:
        ImagePlus: The resulting stack.
    """    
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
    impout.setCalibration(cal)
    return impout
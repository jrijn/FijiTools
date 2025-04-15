# The SpotCropper script is designed to crop a region of interest from
# an input hyperstack, just like the TrackCropper script. However,
# instead of centering on the mean x,y position of the track,
# SpotCropper crops the chosen ROI around each spot in a track. In
# continuous tracks where the tracked object is defined by a spot in
# each sequential frame, like moving particles on a surface, this will
# result in a stack which follows the object through the frames. The
# resulting cropped stacks will be saved in the chosen output directory.
#
# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2020
import ij.IJ as IJ
import ij.measure.ResultsTable as ResultsTable
import os
import ij.WindowManager as WindowManager
# from FijiTools2020.fileHandling import opencsv, getresults
from ij.plugin import Duplicator, Concatenator
# from FijiTools2020.impActions import croppoints, combinestacks

def croppoints(imp, spots, outdir, roi_x=150, roi_y=150, ntracks=None,
               trackid="TRACK_ID", trackxlocation="POSITION_X", trackylocation="POSITION_Y", tracktlocation="FRAME"):
    """Function to follow and crop the individual spots within a
trackmate "Spots statistics.csv" file.

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

    if ntracks == None:
        ntracks = len(spots)
    elif ntracks > len(spots):
        ntracks = len(spots)

    def _cropSingleTrack(ispots):
        """Nested function to crop the spots of a single TRACK_ID.

        Args:
            ispots (list): List of getresults() dictionaries belonging
            to a single track.

        Returns:
            list: A list of ImagePlus stacks of the cropped timeframes.
        """
        outstacks = []

        for j in ispots:

            # Extract all needed row values.
            j_id = int(j[trackid])
            j_x = int(j[trackxlocation] * xScaleMultiplier)
            j_y = int(j[trackylocation] * yScaleMultiplier)
            j_t = int(j[tracktlocation] + 1)

            # Now set an ROI according to the track's xy position in the
            # hyperstack.
            # upper left x, upper left y,roi x dimension, roi y dimension
            imp.setRoi(j_x, j_y, roi_x, roi_y)
            IJ.log("processing frame {}".format(j_t))

            # Optionally, set the correct time position in the stack.
            # This provides cool feedback but is sloooow!
            # imp.setPosition(1, 1, j_t)

            # Crop the ROI on the corresponding timepoint and add to
            # output stack.
            # firstC, lastC, firstZ, lastZ, firstT, lastT
            crop = Duplicator().run(imp, 1, dims[2], 1, dims[3], j_t, j_t)
            outstacks.append(crop)

        return outstacks

    # START OF MAIN FUNCTION.
    # Store the stack dimensions.
    dims = imp.getDimensions()  # width, height, nChannels, nSlices, nFrames
    IJ.log("Dimensions width: {0}, height: {1}, nChannels: {2}, nSlices: {3}, nFrames: {4}.".format(dims[0], dims[1], dims[2], dims[3], dims[4]))

    # Get stack calibration and set the scale multipliers to correct for
    # output in physical units vs. pixels.
    cal = imp.getCalibration()
    if cal.scaled():
        xScaleMultiplier = dims[0]/cal.getX(dims[0])
        yScaleMultiplier = dims[1]/cal.getY(dims[1])
        IJ.log("Physical units to pixel scale: x = {}, y = {} pixels/unit\n".format(xScaleMultiplier, yScaleMultiplier))
    else:
        xScaleMultiplier = 1
        yScaleMultiplier = 1
        IJ.log(
            "Image is not spatially calibrated. Make sure the input .csv isn't either!")
        IJ.log("Physical units to pixel scale: x = {}, y = {} pixels/unit\n".format(xScaleMultiplier, yScaleMultiplier))

    # Add a black frame around the stack to ensure the cropped roi's are
    # never out of view.
    expand_x = dims[0] + roi_x
    expand_y = dims[1] + roi_y

    # This line could be replaced by ij.plugin.CanvasResizer().
    # However, since that function takes ImageStacks, not ImagePlus,
    # that just makes it more difficult for now.
    IJ.run(imp, "Canvas Size...", "width={} height={} position=Center zero".format(expand_x, expand_y))

    # Retrieve all unique track ids. This is what we loop through.
    track_ids = set([track[trackid] for track in spots])
    track_ids = list(track_ids)

    # This loop loops through the unique set of TRACK_IDs from the
    # results table.
    for i in track_ids[0:ntracks]:

        # Extract all spots (rows) with TRACK_ID == i.
        trackspots = [spot for spot in spots if spot[trackid] == i]
        # Monitor progress
        IJ.log("TRACK_ID: {}/{}".format(int(i+1), len(track_ids)))

        # Crop the spot locations of the current TRACK_ID.
        out = _cropSingleTrack(trackspots)

        # Concatenate the frames into one ImagePlus and save.
        out = Concatenator().run(out)
        outfile = os.path.join(outdir, "TRACK_ID_{}.tif".format(int(i)))
        IJ.saveAs(out, "Tiff", outfile)

    IJ.log("\nExecution croppoints() finished.")


def main():
    # Get the wanted output directory and prepare subdirectories for
    # output.
    outdir = IJ.getDirectory("output directory")

    # Open the 'Track statistics.csv' input file and format as
    # getresults() dictionary.
    rt = opencsv()
    rt.deleteRows(0,2)
    rt.show("spots")
    rt = getresults(rt)

    # Retrieve the current image as input (source) image.
    imp = WindowManager.getCurrentImage()

    # Run the main crop function on the source image.
    croppoints(imp, spots=rt, outdir=outdir, roi_x=1100, roi_y=1100, ntracks=1)

    # Combine all output stacks into one movie.
    # combinestacks(outdir, height=8)


# Execute main()
main()

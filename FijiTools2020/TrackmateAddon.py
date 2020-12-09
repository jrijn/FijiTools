import ij.IJ as IJ
import ij.io.Opener as Opener
import ij.ImagePlus as ImagePlus
import ij.ImageStack as ImageStack
import ij.WindowManager as WindowManager
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


class CropTool(object):

    def __init__(self, imp):
        self.imp = imp
        self.tracks = self.opencsv(name="Track statistics.csv")
        self.spots = self.opencsv(name="Spots in tracks statistics.csv")
        self.links = self.opencsv(name="Links in tracks.csv")
        self.croppedpoints = None # Will be populated by croppoints() when called.
        self.croppedtracks = None # Will be populated by croptracks() when called.


    def opencsv(self, name):
        # Return if the csv object was not set.
        # if self.trackscsv == None: return None TODO: some errorchecking for false csv input.

        # Open the csv file and return it as ResultsTable object.
        try:
            csv = IJ.getFilePath("Choose the {} file".format(name))

            if csv.endswith(".csv"): 
                rt = ResultsTable.open(csv)
            else: 
                IJ.log("{} was not a .csv file".format(csv))
                raise ValueError

            columns = rt.getHeadings()
            table = [{column: rt.getValue(column, row) for column in columns} for row in range(rt.size())]
            
            if rt.columnExists("Label"):
                for i in range(len(table)):
                    table[i]["Label"] = rt.getStringValue("Label", i)

            IJ.log("Read {} rows in {}.".format(len(table), name))
            return table

        except Exception as ex:
            IJ.log("Something in opencsv() went wrong: {}".format(type(ex).__name__, ex.args))


    def croppoints(self, outdir, roi_x=150, roi_y=150, ntracks=None,
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

        imp = self.imp
        spots = self.spots
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
        # IJ.log("Dimensions width: {0}, height: {1}, nChannels: {2}, nSlices: {3}, nFrames: {4}.".format(
        #     dims[0], dims[1], dims[2], dims[3], dims[4]))

        # Get stack calibration and set the scale multipliers to correct for output in physical units vs. pixels.
        cal = imp.getCalibration()
        if cal.scaled():
            xScaleMultiplier = cal.pixelWidth
            yScaleMultiplier = cal.pixelHeight
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

        stacks = []
        # This loop loops through the unique set of TRACK_IDs from the results table.
        for i in track_ids[0:ntracks]:
            
            # Extract all spots (rows) with TRACK_ID == i.
            trackspots = [ spot for spot in spots if spot[trackid] == i ]
            # IJ.log ("TRACK_ID: {}/{}".format(int(i+1), len(track_ids))) # Monitor progress

            # Crop the spot locations of the current TRACK_ID.
            out = _cropSingleTrack(trackspots)

            # Concatenate the frames into one ImagePlus and save.
            impout = Concatenator().run(out)
            stacks.append(impout)
            # outfile = os.path.join(outdir, "TRACK_ID_{}.tif".format(int(i)))
            # IJ.saveAs(out, "Tiff", outfile)

        self.croppedpoints = stacks
        IJ.log("\nExecution croppoints() finished.")


    def croptracks(self, outdir, trackid="TRACK_ID",
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

        imp = self.imp
        tracks = self.tracks

        cal = imp.getCalibration()

        stacks = []
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
            # IJ.log("Cropping image with TRACK_ID: {}/{}".format(i_id+1, int(len(tracks))))
            # Duplicator().run(firstC, lastC, firstZ, lastZ, firstT, lastT)
            impout = Duplicator().run(imp, 1, nChannels, 1, nSlices, i_start, i_stop)  
            stacks.append(impout)
            # Save the substack in the output directory
            # outfile = os.path.join(outdir, "TRACK_ID_{}.tif".format(i_id))
            # IJ.saveAs(imp2, "Tiff", outfile)

        self.croppedtracks = stacks
        IJ.log("\nExecution croptracks() finished.")


def main():
    imp = "test.tiff"
    imp = CropTool()
    IJ.log("First TRACK_ID: {}".format(imp.tracks[0]["TRACK_ID"]))


main()

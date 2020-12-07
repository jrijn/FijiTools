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

    def __init__(self):
        self.tracks = self.opencsv(name="Track statistics.csv")
        self.spots = self.opencsv(name="Spots in tracks statistics.csv")
        self.links = self.opencsv(name="Links in tracks.csv")


    def opencsv(self, name):
        # Return if the csv object was not set.
        # if self.trackscsv == None: return None

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


    


def main():
    imp = "test.tiff"
    imp = CropTool()
    IJ.log("First TRACK_ID: {}".format(imp.tracks[0]["TRACK_ID"]))


main()

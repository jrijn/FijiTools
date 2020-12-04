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

    def __init__(self, trackscsv):
        self.trackscsv = trackscsv
        # self.tracks = self.opentracks()
        # self.spotscsv = spotscsv
        # self.spots = self.openspots()

    # def opentracks(self):
    #     # Return if the csv object was not set.
    #     if self.trackscsv == None: return None

    #     # Open the csv file and return it as ResultsTable object.
    #     try:
    #         rt = ResultsTable.open(csv)
    #         columns = rt.getHeadings()
    #         table = [{column: rt.getValue(column, row) for column in columns} for row in range(rt.size())]
            
    #         if rt.columnExists("Label"):
    #             for i in range(len(table)):
    #                 table[i]["Label"] = rt.getStringValue("Label", i)

    #         # IJ.log("Read {} rows in trackscsv.".format(table, len(table)))
    #         return table

    #     except Exception as ex:
    #         IJ.log("Something in opencsv() went wrong: {}".format(type(ex).__name__, ex.args))


    # def openspots(self):
    #     # Return if the csv object was not set.
    #     if self.spotscsv == None: return None

    #     # Open the csv file and return it as ResultsTable object.
    #     try:
    #         rt = ResultsTable.open(csv)
    #         columns = rt.getHeadings()
    #         table = [{column: rt.getValue(column, row) for column in columns} for row in range(rt.size())]
            
    #         if rt.columnExists("Label"):
    #             for i in range(len(table)):
    #                 table[i]["Label"] = rt.getStringValue("Label", i)

    #         # IJ.log("Read {} rows in trackscsv.".format(table, len(table)))
    #         return table

    #     except Exception as ex:
    #         IJ.log("Something in opencsv() went wrong: {}".format(type(ex).__name__, ex.args))



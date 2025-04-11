# Jorik van Rijn <jorik.vanrijn@gmail.com> - 2025

import os
from ij import IJ
from ij.io import Opener, OpenDialog
from ij import ImagePlus
from fiji.threshold import Auto_Threshold
from ij.plugin import ChannelSplitter, ImageCalculator, FolderOpener, RGBStackMerge
from ij.measure import ResultsTable
        
def open_folder_dialog():
    # Call the open method with None to trigger the directory chooser dialog
    imp = FolderOpener.open(None)

    if imp is not None:
        # If a directory was selected and images were loaded, display the stack
        imp.show()
        return imp
    else:
        print("No directory selected or no images loaded.")

def main():

    channels = []

    # channel grey
    imp = open_folder_dialog()
    # channels[0] = Opener.openUsingBioFormats(impath)
    IJ.run(imp, "Enhance Contrast", "saturated=0.35")
    channels.append(imp)
    
    # channel green
    imp = open_folder_dialog()
    # channels[1] = Opener.openUsingBioFormats(impath)
    IJ.run(imp, "Enhance Contrast", "saturated=0.35")
    channels.append(imp)
    
    merge = RGBStackMerge().mergeChannels(channels, True)
    merge.show()

main()

import os
import ij.IJ as IJ
import ij.io.Opener as Opener
import ij.plugin.ChannelSplitter as ChannelSplitter
import ij.plugin.RGBStackMerge as RGBStackMerge
from FijiTools2020.impActions import gaussianFilter, glidingprojection


def main():
    def _saveChannels(channels, name):
        for i,c in enumerate(channels):
            filename = os.path.join(outdir, name + "_C" + str(i+1))
            IJ.saveAs(c, "Tiff", filename)


    # impath = IJ.getFilePath("Choose .ome.tiff file")
    indir = IJ.getDir("Choose input dir")
    outdir = IJ.getDir("Choose output dir")
    files = os.listdir(indir)
    IJ.log("{}".format(files))
    for file in files:
        if file.endswith("tif"):
            filepath = os.path.join(indir, file)
            channels = Opener.openUsingBioFormats(filepath)
            channels = ChannelSplitter.split(channels)
            _saveChannels(channels, file)


main()
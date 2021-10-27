import os
import ij.IJ as IJ
import ij.io.Opener as Opener
import ij.plugin.ChannelSplitter as ChannelSplitter
import ij.plugin.RGBStackMerge as RGBStackMerge
import ij.plugin.ZProjector as ZProjector
import ij.plugin.ImageCalculator as ImageCalculator
import ij.plugin.GaussianBlur3D as GaussianBlur3D
# from FijiTools2020.impActions import subtractzproject, glidingprojection


def zproj(imp):
    # Split channels.
    cal = imp.getCalibration()
    channels = ChannelSplitter().split(imp)
    zproj = [ZProjector.run(c,"max") for c in channels]
  
    # Merge channels.
    merge = RGBStackMerge().mergeChannels(zproj, True) # boolean keep
    merge.setCalibration(cal)
    # IJ.run(merge, "Subtract Background...", "rolling=50 sliding stack")
    # merge.setDisplayMode(IJ.GRAYSCALE)
    # merge.resetDisplayRange()
    return merge


def stackCalc(imp, operation="subtract", c1=2, c2=3):
    # Split channels.
    cal = imp.getCalibration()
    channels = ChannelSplitter().split(imp)

    # Divide channels.
    channels[c1] = ImageCalculator().run(
        "{} 32-bit create stack".format(operation), 
        channels[c1], channels[c2])

    # Merge channels.
    merge = RGBStackMerge().mergeChannels(channels, True) # boolean keep
    merge.setCalibration(cal)
    return merge


def main():
    # Open an .ome.tif image from the Flexoscope.
    imdir = IJ.getDir("Choose .ome.tiff files")
    outdir = IJ.getDir("Choose .ome.tiff files")

    for root, dirs, files in os.walk(imdir, topdown=False):
       for name in files:
           if name.endswith(".ome.tif"):
               impath = os.path.join(root, name)
               imp = Opener.openUsingBioFormats(impath)

               # Correct cross-excitation.
               imp = stackCalc(imp, "subtract", 2, 3)

               # Remove background.
               gaussian = imp.duplicate()
               GaussianBlur3D.blur(gaussian, 20, 20, 1)
               imp = ImageCalculator().run("divide 32-bit create stack", 
                                           imp, gaussian)

               # Make z-projection.
               ZProjector.run(imp,"max")

               IJ.log("{}".format(name))
               outpath = os.path.join(outdir, name)
               IJ.saveAs(imp, "Tiff", outpath)


main()
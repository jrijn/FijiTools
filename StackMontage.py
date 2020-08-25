import os
import ij.IJ as IJ
import ij.io.Opener as Opener
from FijiTools2020.fileHandling import saveimage
from FijiTools2020.impActions import makemontage


def main():
    # Get the wanted input and output directories.
    indir = IJ.getDirectory("input directory")
    outdir = IJ.getDirectory("output directory")

    # Collect all files in the import directory and sort on file name.
    files = sorted(os.listdir(indir))

    # Loop through all input files.
    montages = []
    for imfile in files:

        # Some optional feedback if you're impatient.
    	IJ.log("File: {}/{}".format(files.index(imfile)+1, len(files)))
        
        # Make montage of every .tiff file and save as .tiff in the output directory.
        if imfile.endswith(".tif"):
            imp = Opener().openImage(indir, imfile)
            montage = makemontage(imp, hsize=6, vsize=6, increment=2)
            saveimage(montage, outdir)


main()
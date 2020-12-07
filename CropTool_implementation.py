from FijiTools2020.TrackmateAddon import CropTool
import ij.IJ as IJ
import ij.WindowManager as WindowManager

imp = WindowManager.getCurrentImage()
csv = IJ.getFilePath("Choose a .csv file")
imp = CropTool(imp, trackscsv=csv)
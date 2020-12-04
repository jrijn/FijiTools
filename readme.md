# FijiTools2020

## Introduction

FijiTools2020 is a collection of tools designed for use in ImageJ/Fiji. Most of them are meant to work in conjunction with a separately performed Trackmate analysis.

## Installation

Copy the folder "FijiTools2020" to your local copy of Fiji/ImageJ, in the folder Fiji.app/jars/Lib or Imagej.app/jars/Lib. The scripts TrackCropper.py, SpotCropper.py and others can then be opened in ImageJ, by drag-and-dropping them on the statusbar. Press "run" to let the scripts do their magic!

## Scripts

More information about the various application scripts bundled in this repository.

### StackMontage

This script takes an input directory with a number of (hyper)stacks. Each input stack will be formatted as a montage with the chosen dimensions and frame interval. The resulting montage images are saved in the chosen output directory.

### FlexoscopeFormatter

This script is used for routine processing of two-channel stacks from the flexoscope in the Sellin lab. The first (DIC) channel is filtered to remove non-mobile background using a medianfilter. The second (fluorescent bacteria) channel is filtered to remove all swimming bacteria using a gliding median projection of every 3 frames.

## TrackMate helper scripts

These scripts are meant to be used in conjunction with the exported analysis .csv files from an earlier performed TrackMate analysis. Typically, these .csv files are called: 'Spots in tracks statistics.csv', 'Links in tracks statistics.csv', and 'Track statistics.csv'.

### TrackCropper

The TrackCropper script is designed to crop a region of interest from an input hyperstack. The size of the ROI can be set manually, and will be centered around the x,y position of each individual track. The resulting cropped stacks will be saved in the chosen output directory.

### SpotCropper

The SpotCropper script is designed to crop a region of interest from an input hyperstack, just like the TrackCropper script. However, instead of centering on the mean x,y position of the track, SpotCropper crops the chosen ROI around each spot in a track. In continuous tracks where the tracked object is defined by a spot in each sequential frame, like moving particles on a surface, this will result in a stack which follows the object through the frames. The resulting cropped stacks will be saved in the chosen output directory.



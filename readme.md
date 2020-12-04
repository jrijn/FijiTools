# FijiTools2020

[TOC]

---

## Introduction

FijiTools2020 is a collection of tools designed for use in ImageJ/Fiji. Most of them are meant to work in conjunction with a separately performed Trackmate analysis.

## Installation

Copy the folder "FijiTools2020" to your local copy of Fiji/ImageJ, in the folder Fiji.app/jars/Lib or Imagej.app/jars/Lib. The scripts TrackCropper.py, SpotCropper.py and others can then be opened in ImageJ, by drag-and-dropping them on the statusbar. Press "run" to let the scripts do their magic!

## TrackCropper

...

## SpotCropper

...

## StackMontage

...

## FlexoscopeFormatter

This script is used for routine processing of two-channel stacks from the flexoscope in the Sellin lab. The first (DIC) channel is filtered to remove non-mobile background using a medianfilter. The second (fluorescent bacteria) channel is filtered to remove all swimming bacteria using a gliding median projection of every 3 frames.

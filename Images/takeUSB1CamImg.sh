#!/bin/bash
imgPath=$1
echo "Taking USB1-Camera pic.."
fswebcam -p YUYV -d /dev/video1 -r 640x480 --no-banner $imgPath
echo "done taking USB1-pic!"

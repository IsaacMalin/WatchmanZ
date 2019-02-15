#!/bin/bash

vidPath=$1
vidLength=$2

echo "Taking $vidLength ms long video.."

/home/pi/Watchman/checkLDR.py
raspivid -t $vidLength -w 640 -h 480 -fps 25 -b 1200000 -p 0,0,640,480 -o pivideo.h264
/home/pi/Watchman/resetIR.py
MP4Box -add pivideo.h264 $vidPath
rm pivideo.h264

echo "done taking PiCam-video"

#!/bin/bash

vidPath=$1
vidLength=$2
state=$(cat '/home/pi/Watchman/Videos/takePiCamVid.txt')
#echo $state
if [ "$state" = "1" ];
then
echo "Already taking PiCam-video"
else
echo "Taking $vidLength ms long video.."
echo '1' > /home/pi/Watchman/Videos/takePiCamVid.txt
#/home/pi/Watchman/checkLDR.py
raspivid -t $vidLength -w 640 -h 480 -fps 25 -b 1200000 -p 0,0,640,480 -o pivideo.h264
#/home/pi/Watchman/resetIR.py
MP4Box -add pivideo.h264 $vidPath
rm pivideo.h264

echo "done taking PiCam-video"
echo '0' > /home/pi/Watchman/Videos/takePiCamVid.txt
fi

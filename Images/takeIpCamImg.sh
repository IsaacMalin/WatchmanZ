#!/bin/bash
  imgPath=$1
  ipAddress=$2
  echo "Taking pic from IP Camera - $ipAddress.."
#  /home/pi/Watchman/checkLDR.py
  ffmpeg -f MJPEG -y -i http://$ipAddress:81/stream -r 1 -vframes 1 -q:v 1 $imgPath
#  /home/pi/Watchman/resetIR.py
  echo "done taking ip camera pic!"







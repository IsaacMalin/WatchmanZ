#!/bin/bash
  imgPath=$1
  echo "Taking Pi-Camera pic.."
#  /home/pi/Watchman/checkLDR.py
  raspistill -o $imgPath
#  /home/pi/Watchman/resetIR.py
  echo "done taking Pi-pic!"

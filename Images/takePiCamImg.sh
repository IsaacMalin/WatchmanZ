#!/bin/bash
  imgPath=$1
  state=$(cat '/home/pi/Watchman/Images/takePiCamImg.txt')
#  echo $state
  if [ "$state" = "1" ];
  then
  echo "Already taking Pi-Camera pic.."
  else
  echo '1' > /home/pi/Watchman/Images/takePiCamImg.txt
  echo "Taking Pi-Camera pic.."
  raspistill -w 1024 -h 768 --annotate 12 -o $imgPath
  echo "done taking Pi-pic!"
  echo '0' > /home/pi/Watchman/Images/takePiCamImg.txt
  fi

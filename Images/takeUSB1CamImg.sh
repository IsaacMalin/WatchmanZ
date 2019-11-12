#!/bin/bash
imgPath=$1
state=$(cat '/home/pi/Watchman/Images/takeUSB1CamImg.txt')
#echo $state
if [ "$state" = "1" ];
then
echo "Already taking USB1-Camera pic.."
else
echo '1' > /home/pi/Watchman/Images/takeUSB1CamImg.txt
echo "Taking USB1-Camera pic.."
fswebcam -p YUYV -d /dev/video1 -r 640x480 --no-banner $imgPath
echo "done taking USB1-pic!"
echo '0' > /home/pi/Watchman/Images/takeUSB1CamImg.txt
fi

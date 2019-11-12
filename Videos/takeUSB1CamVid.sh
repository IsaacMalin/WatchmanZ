#!/bin/bash
vidPath=$1
vidLength=$2
state=$(cat '/home/pi/Watchman/Videos/takeUSB1CamVid.txt')
#echo $state
if [ "$state" = "1" ];
then
echo "Already taking PiCam-video"
else
echo "Taking $vidLength sec long video.."
echo '1' > /home/pi/Watchman/Videos/takeUSB1CamVid.txt
avconv -t $vidLength -f video4linux2 -s 640x480 -i /dev/video1 $vidPath
echo "done taking USB1-video"
echo '0' > /home/pi/Watchman/Videos/takeUSB1CamVid.txt
fi

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
#fswebcam -p YUYV -d /dev/video1 -r 640x480 --timestamp "%Y-%m-%d %H:%M" $imgPath
ffmpeg -f video4linux2 -i /dev/video1 -vframes 1 -vf "drawtext=fontfile=/Windows/Fonts/Arial.ttf: text='%{localtime}': x=(w-tw)/2: y=h-(2*lh): fontcolor=white: box=1: boxcolor=0x00000000@1: fontsize=20" -y $imgPath
echo "done taking USB1-pic!"
echo '0' > /home/pi/Watchman/Images/takeUSB1CamImg.txt
fi

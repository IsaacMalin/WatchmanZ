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
#avconv -t $vidLength -f video4linux2 -s 640x480 -i /dev/video1 $vidPath
ffmpeg -i /dev/video1 -vf "drawtext=fontfile=/Windows/Fonts/Arial.ttf: text='%{localtime}': x=(w-tw)/2: y=h-(2*lh): fontcolor=white: box=1: boxcolor=0x00000000@1: fontsize=20" -b:v 100k -c:v libx264 -pix_fmt yuvj420p -preset ultrafast -r 15 -t $vidLength -y $vidPath
echo "done taking USB1-video"
echo '0' > /home/pi/Watchman/Videos/takeUSB1CamVid.txt
fi

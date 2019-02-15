#!/bin/bash
vidPath=$1
vidLength=$2
echo "Taking $vidLength sec long video.."
avconv -t $vidLength -f video4linux2 -s 640x480 -i /dev/video0 $vidPath
echo "done taking USB1-video"

#!/bin/bash
vidPath=$1
vidLength=$2
ipAddress=$3
echo "Taking $vidLength sec long video from ip camera - $ipAddress.."
ffmpeg -f MJPEG -i "http://$ipAddress:81/stream" -filter:v "setpts=5.0*PTS" -t $vidLength -c:v libx264 -pix_fmt yuvj420p -b:v 192k -preset ultrafast -y $vidPath
echo "done taking IP-video"


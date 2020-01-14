#!/bin/sh

$ssid

ssid=Connecting
ssid=$(/home/pi/Watchman/wifiSSID.py)

state=$(cat '/home/pi/Watchman/wifiConnected.txt')
echo $state
if [ "$state" = "1" ];
  then
  echo "Script already running"
else
  echo '1' > /home/pi/Watchman/wifiConnected.txt

  ip=$(hostname -I)
  IFS='.'
  set -f
  set -- $ip
  shortip="[.$3.$4]"
  /home/pi/Watchman/ssd1306/display.py "$ssid $shortip" 4

  echo '0' > /home/pi/Watchman/wifiConnected.txt
fi

#!/bin/sh
# redirect all output into a logfile
exec 1>> /home/pi/Watchman/logs/onWifiConnect.log 2>&1

case "$1" in
wlan0)
    case "$2" in
    CONNECTED)
        touch /home/pi/Watchman/wifiConnected.txt
        state=$(cat '/home/pi/Watchman/wifiConnected.txt')
        if [ $state = '0' ]
        then
          echo '1' > /home/pi/Watchman/wifiConnected.txt
          # do stuff on connect with wlan0
          ssid=Connecting
          /home/pi/Watchman/ssd1306/display.py $ssid 4
          sleep 10s
          ssid=$(/home/pi/Watchman/wifiSSID.py)
          ip=$(hostname -I)
          IFS='.'
          set -f
          set -- $ip
          shortip="[.$3.$4]"
          /home/pi/Watchman/ssd1306/display.py "$ssid $shortip" 4
          /home/pi/Watchman/TelegramBot/TelegramSendMsg.py "Connection to WiFi [$ssid] is now active." "0"
          echo '0' > /home/pi/Watchman/wifiConnected.txt
        else
          echo "Already alerting about connection"
        fi
        ;;
    DISCONNECTED)
        touch /home/pi/Watchman/wifiDisconnected.txt
        state=$(cat '/home/pi/Watchman/wifiDisconnected.txt')
        if [ $state = '0' ]
        then
          echo '1' > /home/pi/Watchman/wifiDisconnected.txt
          # do stuff on disconnect with wlan0
          /home/pi/Watchman/ssd1306/display.py Disconnected 4
          /home/pi/Watchman/sendSMS.py "WiFi is disconnected"
          sleep 10s
          echo '0' > /home/pi/Watchman/wifiDisconnected.txt
        else
          echo "Already alerting about disconnection"
        fi
        ;;
    *)
        >&2 echo empty or undefined event for wlan0: "$2"
        exit 1
        ;;
    esac
    ;;

wlan1)
    case "$2" in
    CONNECTED)
        # do stuff on connect with wlan1
        echo wlan1 connected
        ;;
    DISCONNECTED)
        # do stuff on disconnect with wlan1
        echo wlan1 disconnected
        ;;
    *)
        >&2 echo empty or undefined event for wlan1: "$2"
        exit 1
        ;;
    esac
    ;;

*)
    >&2 echo empty or undefined interface: "$1"
    exit 1
    ;;
esac

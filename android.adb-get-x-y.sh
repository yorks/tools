#!/bin/sh
set -e
echo -n "正在获取手机屏幕分辨率... "
WH=$(adb shell wm size|awk '{print $NF}')
W=$(echo "$WH" | awk -F'x' '{print $1}')
H=$(echo "$WH" | awk -F'x' '{print $2}')
echo "done $W x $H"

echo -n "正在获取手机的event分辨率... "
eWH=$(adb shell getevent -p | egrep "0035|0036")
eW=$(echo "$eWH" | egrep -o 'max [0-9]+,' | egrep -o '[0-9]+'|head -n1)
eH=$(echo "$eWH" | egrep -o 'max [0-9]+,' | egrep -o '[0-9]+'|tail -n1)
echo "done $eW x $eH"

rateW=$(echo "$W $eW" | awk '{print $1/$2}')
rateH=$(echo "$H $eH" | awk '{print $1/$2}')
echo "ratew: $rateW, rateH: $rateH"

adb shell getevent -p | egrep 'add device|name:'
echo "请参考上面的内容，输入屏幕设备的路径，默认是[/dev/input/event1]:"
read dev
[[ "x$dev" == "x" ]] && dev="/dev/input/event1"


while sleep 1; do 
echo -n  "请点击手机屏幕以便获取坐标.... "
adb shell getevent -c 10 $dev | awk '$2 ~ /^003[5-6]$/' > /tmp/.$0.event.log
e35=$(cat /tmp/.$0.event.log| awk '$2=="0035" {print strtonum("0x"$NF)}'|head -n 1)
e36=$(cat /tmp/.$0.event.log| awk '$2=="0036" {print strtonum("0x"$NF)}'|head -n 1)
x=$(echo $e35 $rateW | awk '{print $1*$2}')
y=$(echo $e36 $rateH | awk '{print $1*$2}')
echo "done, x y: $x $y , CTRL+c 退出 "
done

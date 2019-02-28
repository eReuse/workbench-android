#!/usr/bin/env bash
echo 'This requires "adb" installed.'
echo 'If it says "no devices/emulators... it means that the Android:'
echo '- Is not plugged in or it had a micro cut. Check cable and try again.'
echo '- You have not given access to adb. Check https://developer.android.com/studio/command-line/adb#Enabling'
echo '"Cant find service" errors are ok.'
echo ''
m=$(adb shell getprop ro.product.model)
# trim From https://stackoverflow.com/a/3232433/2710757
model=$(echo -e "${m}" | tr -d '[:space:]')
mkdir -p $model
echo "Generating files for $model..."
adb shell getprop > "$model/getprop.$model.txt"
adb shell dumpsys > "$model/dumpsys.$model.txt"
adb shell dumpsys meminfo -c > "$model/meminfo.dumpsys.$model.txt"
adb shell cat /proc/meminfo > "$model/meminfo.$model.txt"
adb shell dumpsys battery > "$model/battery.dumpsys.$model.txt"
adb shell dumpsys batterymanager > "$model/batterymanager.dumpsys.$model.txt"
adb shell ls /sys/devices/system/cpu > "$model/cpu-ls.$model.txt"
adb shell ip addr show > "$model/ip.$model.txt"
adb shell settings get secure bluetooth_address > "$model/bluetooth_address.$model.txt"
echo "Done. Files are in $model directory."

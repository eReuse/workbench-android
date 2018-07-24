#!/bin/bash

clean_usb_list_file="/tmp/clean_lsusb"
plugged_usb_list_file="/tmp/plugged_lsusb"
android_usb_list_file="/tmp/android_lsusb"

press_key_message=" and press \"Enter\" key to continue..."

android_rules_file="/etc/udev/rules.d/51-android.rules"

create_adb_device_rule () { 
 prefix="SUBSYSTEM==\\\"usb\\\", ATTR\\\{idVendor\\\}==\\\""
 inner="\\\", ATTR\{idProduct\\\}==\\\""
 suffix="\\\", MODE=\\\"0666\\\", GROUP=\\\"plugdev\\\""
 echo ${prefix}${1}${inner}${2}${suffix}
}

clear

echo "Remove all Android devices plugged to this PC"${press_key_message}
read key
lsusb > $clean_usb_list_file

echo "Now, plug again the Android devices"${press_key_message}
read key
sleep 5s
lsusb > $plugged_usb_list_file

diff $plugged_usb_list_file $clean_usb_list_file | grep '<' | cut -c3- > ${android_usb_list_file}

num_devices_found=`wc -l ${android_usb_list_file} | cut -d ' ' -f 1`
echo ${num_devices_found}" devices found!"  

if [ ${num_devices_found} -eq 0 ]
then
	exit
fi
sudo touch ${android_rules_file}
cat ${android_usb_list_file} | while read line
do
	device_codification=`echo ${line} | cut -d ' ' -f6`
        device_description=`echo ${line} | cut -d ' ' -f7-`
	device_vendor_id=`echo ${device_codification} | cut -d ':' -f1`
	device_model_id=`echo ${device_codification} | cut -d ':' -f2`

	echo "Processing device:"
	echo "\tDescription:\t${device_description}"
	echo "\tVendor:\t\t${device_vendor_id}"
	echo "\tModel:\t\t${device_model_id}"

	if [ `grep -e \"${device_vendor_id}\.\*${device_model_id}\" ${android_rules_file}  | wc -l` -gt 0 ]
	then
		echo "Device already known by ADB"
	else
		echo "Adding new device to ADB devices list..."
		new_rule_line=`create_adb_device_rule ${device_vendor_id} ${device_model_id}`
		echo ${new_rule_line}
		sudo sh -c "echo ${new_rule_line} >> ${android_rules_file}"
	fi

done

echo "In each connected device, bootloader menu will be shown, now you have to select \"wipe-data recovery\" option to hard-reset your device"
echo "Rebooting Android devices..."
adb reboot recovery


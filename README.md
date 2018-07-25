# Workbench-Android

__Only works with samsung GT-I9195__

Manages the installation of a new Android OS (Lineage) after doing steps to securely delete bit per bit any data of the last owner.

Execute `python script` to start the process.

- [x] 1 Boot the device into bootloader.
- [x] 2 Flash recovery with `heimdall`.
- [ ] 3 Get device info through usb protocol.
- [ ] 4 Reboot into recovery.
- [x] 5 Get device information.
- [ ] 6 Wipe user data.
- [ ] 7 Flash new rom.

## Contents of this project.

    workbrench-android/
    |-- workbrench_android/
    |   |-- __init__.py
    |   |-- workbrench_android.py  # Mangaes adb and heimdall
    |
    |-- script.py  # Main script to execute.
    |-- README

## How to flash:

    heimdall flash --RECOVERY filename.img 

## ADB commands

### $ adb shell recovery

    --send_intent=anystring - write the text out to recovery.intent
    --update_package=path - verify install an2 OTA package file
    --wipe_data - erase user data (and cache), then reboot
    --wipe_cache - wipe cache (but not user data), then reboot
    --set_encrypted_filesystem=on|off - enables / diasables encrypted fs


### Get properties

https://stackoverflow.com/questions/22092118/get-device-information-such-as-product-model-from-adb-command#

    adb -s 123abc12 shell getprop ro.product.model
    
Result example:

    [audio.offload.disable]: [1]
    [camera2.portability.force_api]: [1]
    [dalvik.vm.appimageformat]: [lz4]
    [dalvik.vm.dex2oat-Xms]: [64m]
    [dalvik.vm.dex2oat-Xmx]: [512m]
    [dalvik.vm.dex2oat-swap]: [false]
    [dalvik.vm.heapgrowthlimit]: [192m]
    [dalvik.vm.heapmaxfree]: [8m]
    [dalvik.vm.heapminfree]: [2m]
    [dalvik.vm.heapsize]: [256m]
    [dalvik.vm.heapstartsize]: [8m]
    [dalvik.vm.heaptargetutilization]: [0.75]
    [dalvik.vm.image-dex2oat-Xms]: [64m]
    [dalvik.vm.image-dex2oat-Xmx]: [64m]
    [dalvik.vm.isa.arm.features]: [default]
    [dalvik.vm.isa.arm.variant]: [krait]
    [dalvik.vm.lockprof.threshold]: [500]
    [dalvik.vm.stack-trace-file]: [/data/anr/traces.txt]
    [dalvik.vm.usejit]: [true]
    [dalvik.vm.usejitprofiles]: [true]
    [debug.atrace.tags.enableflags]: [0]
    [debug.composition.type]: [c2d]
    [debug.mdpcomp.logs]: [0]
    [debug.sf.hw]: [1]
    [init.svc.adbd]: [running]
    [init.svc.recovery]: [running]
    [init.svc.set_permissive]: [stopped]
    [init.svc.ueventd]: [running]
    [keyguard.no_require_sim]: [true]
    [media.aac_51_output_enabled]: [true]
    [media.sf.extractor-plugin]: [libffmpeg_extractor.so]
    [media.sf.omx-plugin]: [libffmpeg_omx.so]
    [media.stagefright.legacyencoder]: [true]
    [media.stagefright.less-secure]: [true]
    [mm.enable.smoothstreaming]: [true]
    [mtp.crash_check]: [0]
    [net.bt.name]: [Android]
    [net.change]: [net.bt.name]
    [persist.debug.wfd.enable]: [1]
    [persist.gps.qc_nlp_in_use]: [1]
    [persist.gps.qmienabled]: [true]
    [persist.hwc.mdpcomp.enable]: [true]
    [persist.radio.add_power_save]: [1]
    [persist.service.adb.enable]: [1]
    [persist.sys.dalvik.vm.lib.2]: [libart.so]
    [persist.sys.dun.override]: [0]
    [persist.sys.usb.config]: [adb]
    [persist.sys.wfd.virtual]: [0]
    [persist.timed.enable]: [true]
    [pm.dexopt.ab-ota]: [speed-profile]
    [pm.dexopt.bg-dexopt]: [speed-profile]
    [pm.dexopt.boot]: [verify-profile]
    [pm.dexopt.core-app]: [speed]
    [pm.dexopt.first-boot]: [interpret-only]
    [pm.dexopt.forced-dexopt]: [speed]
    [pm.dexopt.install]: [interpret-only]
    [pm.dexopt.nsys-library]: [speed]
    [pm.dexopt.shared-apk]: [speed]
    [qcom.bluetooth.soc]: [smd]
    [rild.libargs]: [-d /dev/smd0]
    [rild.libpath]: [/system/lib/libsec-ril.so]
    [ro.adb.secure]: [0]
    [ro.allow.mock.location]: [0]
    [ro.am.reschedule_service]: [true]
    [ro.baseband]: [msm]
    [ro.board.platform]: [msm8960]
    [ro.boot.baseband]: [msm]
    [ro.boot.batt_check_recovery]: [1]
    [ro.boot.boot_recovery]: [1]
    [ro.boot.bootdevice]: [msm_sdcc.1]
    [ro.boot.bootloader]: [I9195XXUCPD1]
    [ro.boot.cp_debug_level]: [0x55FF]
    [ro.boot.csb_val]: [1]
    [ro.boot.debug_level]: [0x4f4c]
    [ro.boot.emmc]: [true]
    [ro.boot.emmc_checksum]: [3]
    [ro.boot.hardware]: [qcom]
    [ro.boot.nvdata_backup]: [0]
    [ro.boot.serialno]: [21f4c3ce]
    [ro.boot.warranty_bit]: [1]
    [ro.bootimage.build.date.utc]: [1512536043]
    [ro.bootimage.build.date]: [mercredi 6 décembre 2017, 05:54:03 (UTC+0100)]
    [ro.bootloader]: [I9195XXUCPD1]
    [ro.bootmode]: [unknown]
    [ro.build.characteristics]: [default]
    [ro.build.date.utc]: [1512536043]
    [ro.build.date]: [mercredi 6 décembre 2017, 05:54:03 (UTC+0100)]
    [ro.build.description]: [serranoltexx-user 4.4.2 KOT49H I9195XXUCNE6 release-keys]
    [ro.build.display.id]: [lineage_serranoltexx-userdebug 7.1.2 NJH47F 3f728db964 test-keys]
    [ro.build.fingerprint]: [samsung/serranoltexx/serranolte:4.4.2/KOT49H/I9195XXUCNE6:user/release-keys]
    [ro.build.flavor]: [lineage_serranoltexx-userdebug]
    [ro.build.host]: [LM-217]
    [ro.build.id]: [NJH47F]
    [ro.build.product]: [serranolte]
    [ro.build.selinux]: [1]
    [ro.build.tags]: [test-keys]
    [ro.build.type]: [userdebug]
    [ro.build.user]: [ne0zone75]
    [ro.build.version.all_codenames]: [REL]
    [ro.build.version.base_os]: []
    [ro.build.version.codename]: [REL]
    [ro.build.version.incremental]: [3f728db964]
    [ro.build.version.preview_sdk]: [0]
    [ro.build.version.release]: [7.1.2]
    [ro.build.version.sdk]: [25]
    [ro.build.version.security_patch]: [2017-11-06]
    [ro.carrier]: [unknown]
    [ro.chipname]: [MSM8930AB]
    [ro.cm.build.version.plat.rev]: [0]
    [ro.cm.build.version.plat.sdk]: [7]
    [ro.cm.build.version]: [14.1]
    [ro.cm.device]: [serranoltexx]
    [ro.cm.display.version]: [14.1-20171206_045403-UNOFFICIAL-serranoltexx]
    [ro.cm.releasetype]: [UNOFFICIAL]
    [ro.cm.version]: [14.1-20171206_045403-UNOFFICIAL-serranoltexx]
    [ro.cmlegal.url]: [https://lineageos.org/legal]
    [ro.com.android.mobiledata]: [false]
    [ro.com.google.clientidbase]: [android-google]
    [ro.config.alarm_alert]: [Hassium.ogg]
    [ro.config.notification_sound]: [Argon.ogg]
    [ro.config.ringtone]: [Orion.ogg]
    [ro.dalvik.vm.native.bridge]: [0]
    [ro.debuggable]: [1]
    [ro.device.cache_dir]: [/cache]
    [ro.gps.agps_provider]: [1]
    [ro.hardware]: [qcom]
    [ro.hwui.text_large_cache_height]: [2048]
    [ro.modversion]: [14.1-20171206_045403-UNOFFICIAL-serranoltexx]
    [ro.opengles.version]: [196608]
    [ro.product.board]: [MSM8960]
    [ro.product.brand]: [samsung]
    [ro.product.cpu.abi2]: [armeabi]
    [ro.product.cpu.abi]: [armeabi-v7a]
    [ro.product.cpu.abilist32]: [armeabi-v7a,armeabi]
    [ro.product.cpu.abilist64]: []
    [ro.product.cpu.abilist]: [armeabi-v7a,armeabi]
    [ro.product.device]: [serranolte]
    [ro.product.locale]: [en-US]
    [ro.product.manufacturer]: [Samsung]
    [ro.product.model]: [GT-I9195]
    [ro.product.name]: [lineage_serranoltexx]
    [ro.product_ship]: [true]
    [ro.qc.sdk.izat.premium_enabled]: [0]
    [ro.qc.sdk.izat.service_mask]: [0x0]
    [ro.qualcomm.bt.hci_transport]: [smd]
    [ro.qualcomm.cabl]: [0]
    [ro.recovery_id]: [0x1a21114fd141ff566fd6ddbfedc064e3b9ec0c06000000000000000000000000]
    [ro.revision]: [0]
    [ro.ril.telephony.mqanelements]: [6]
    [ro.secure]: [0]
    [ro.serialno]: [21f4c3ce]
    [ro.sf.lcd_density]: [240]
    [ro.storage_manager.enabled]: [true]
    [ro.sys.fw.dex2oat_thread_count]: [4]
    [ro.telephony.call_ring.multiple]: [0]
    [ro.telephony.default_network]: [3]
    [ro.telephony.ril_class]: [SerranoRIL]
    [ro.twrp.boot]: [1]
    [ro.twrp.version]: [3.2.0-1-0]
    [ro.vendor.extension_library]: [libqti-perfd-client.so]
    [ro.warmboot.capability]: [1]
    [ro.wifi.channels]: []
    [ro.zygote]: [zygote32]
    [security.perf_harden]: [1]
    [service.adb.root]: [1]
    [sys.usb.config]: [mtp,adb]
    [telephony.lteOnGsmDevice]: [1]
    [twrp.action_complete]: [0]
    [twrp.crash_counter]: [0]
    [use.dedicated.device.for.voip]: [true]
    [use.voice.path.for.pcm.voip]: [true]
    [wifi.interface]: [wlan0]

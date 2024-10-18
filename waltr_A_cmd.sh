#!/bin/sh

python3 -m esptool -p /dev/ttyUSB0 -b 460800 --before default_reset --after hard_reset --chip esp32 write_flash --flash_mode dio --flash_size detect --flash_freq 40m 0x1000 ~/waltr/firmware/waltr_A_0410_0447/WAW_4.1_v4.47.ino.bootloader.bin 0x8000 ~/waltr/firmware/waltr_A_0410_0447/WAW_4.1_v4.47.ino.partitions.bin 0x10000 ~/waltr/firmware/waltr_A_0410_0447/WAW_4.1_v4.47.ino.bin

#!/usr/bin/env python3

# ----------------------------------------------------------------------------------------------------------------------------------------------
# File: updater.py
# Created Date: Monday, May 6th 2024, 3:31:09 pm
# Author: Florian
# Description: Update the firmware of the STM32 on the hardware controller of the Mobi.
# ----------------------------------------------------------------------------------------------------------------------------------------------

import subprocess
import sys
from logging import INFO
import requests
from tempfile import TemporaryDirectory
from tqdm import tqdm
from argparse import ArgumentParser
from os import path
import os


temp_dir: TemporaryDirectory = None


def get_current_version_from_github():
    res = requests.get(
        "https://api.github.com/repos/FHWN-Robotik/MobiController-MicroROS-Firmware/releases/latest"
    )

    data = res.json()
    version = data.get("tag_name")
    return version


def download_current_firmware():
    global temp_dir
    url = "https://github.com/FHWN-Robotik/MobiController-MicroROS-Firmware/releases/latest/download/micro_ros_firmware.bin"
    file_name = "micro_ros_firmware.bin"
    temp_dir = TemporaryDirectory()
    file_path = os.path.join(temp_dir.name, file_name)

    res = requests.get(url, stream=True)
    total_size_in_bytes = int(res.headers.get("content-length", 0))
    block_size = 1024  # 1 Kibibyte

    progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)

    if res.ok:
        # print("saving to", os.path.abspath(file_path))
        with open(file_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
                    progress_bar.update(len(chunk))

        progress_bar.close()
        return file_path
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(res.status_code, res.text))
        return None


def parse_args(parser: ArgumentParser):
    parser.add_argument(
        "-b",
        "--binary",
        type=str,
        help="Flash a custom .bin file, instead of downloading it from GitHub.",
    )

    return parser.parse_args()


def main():
    global min_mon
    parser = ArgumentParser(
        prog="updater.py",
        description="Update the firmware of the MobiController STM32.",
    )
    args = parse_args(parser)

    firmware_bin_path = None

    if not args.binary:
        current_version = get_current_version_from_github()
        print(f"Updating the firmware to {current_version}")

    else:
        firmware_bin_path = path.abspath(args.binary)
        print(f"Flashing binary from: {firmware_bin_path}")

    do_update = input("Do you want to update? [y/N]: ").lower()
    if do_update != "y" and do_update != "j":
        bye()
        return

    print("Please boot the controller into DFU mode.\n To do so, hold the 'USER_BTN' button and press the 'RESET' button.")
    input("Press [enter] when the controller is in DFU mode.")

    if not args.binary:
        firmware_bin_path = download_current_firmware()

    if not firmware_bin_path:
        print("Error downloading the firmware!")
        bye()
        return

    # dfu-util -a 0 -D ./micro_ros_firmware.bin -s 0x08000000:leave
    subprocess.run(
        ["dfu-util", "-a", "0", "-D", firmware_bin_path, "-s", "0x08000000:leave"]
    )
    bye()


def bye():
    global temp_dir
    if temp_dir:
        temp_dir.cleanup()
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        bye()

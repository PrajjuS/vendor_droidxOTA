#!/usr/bin/env python
#
# Python code which automatically posts Message in a Telegram Group if any new update is found.
# Intended to be run on every push
# USAGE : python3 post.py
# See README for more.
#
# Copyright (C) 2024 PrajjuS <theprajjus@gmail.com>
#
# Credits: Ashwin DS <astroashwin@outlook.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation;
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import requests
import telebot
import os
import json
import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
from NoobStuffs.libtelegraph import TelegraphHelper

# Get configs from workflow secrets
def getConfig(config_name: str):
    return os.getenv(config_name)
try:
    BOT_TOKEN = getConfig("BOT_TOKEN")
    CHAT_ID = getConfig("CHAT_ID")
    BANNER_URL = getConfig("BANNER_URL")
except KeyError:
    print("Fill all the configs plox..\nExiting...")
    exit(0)

# Init bot
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Init telegraph
telegraph = TelegraphHelper("Project-Matrixx", "https://t.me/ProjectMatrixx_bot") 

# File directories
jsonDir = "builds" 
idDir = ".github/scripts"

# Store IDs in a file to compare
def update(IDs):
    with open(f"{idDir}/file_ids.txt", "w+") as log:
        for ids in IDs:
            log.write(f"{str(ids)}\n")

# Return IDs of all latest files from json files
def get_new_id():
    files = []
    file_id = []    
    for all in os.listdir(jsonDir):
        if all.endswith('.json'):
            files.append(all)
    for all_files in files:
        with open(f"{jsonDir}/{all_files}", "r") as file:
            data = json.loads(file.read())['response'][0]
            file_id.append(data['sha256'])
    return file_id

# Return previous IDs
def get_old_id():
    old_id = []
    with open(f"{idDir}/file_ids.txt", "r") as log:
        for ids in log.readlines():
            old_id.append(ids.replace("\n", ""))
    return old_id

# Remove elements in 2nd list from 1st, helps to find out which device got an update
def get_diff(new_id, old_id):
    first_set = set(new_id)
    sec_set = set(old_id)
    return list(first_set - sec_set)

# Grab needed info using ID of the file
def get_info(ID):
    files = []
    for all in os.listdir(jsonDir):
        if all.endswith('.json'):
            files.append(all)
    for all_files in files:
        with open(f"{jsonDir}/{all_files}", "r") as file:
            data = json.loads(file.read())['response'][0]
            if data['sha256'] == ID:
                device = all_files
                break
    with open(f"{jsonDir}/{device}") as device_file:
        info = json.loads(device_file.read())['response'][0]
        OEM = info['oem']
        DEVICE_NAME = info['device']
        DEVICE_CODENAME = device.split('.')[0]
        MAINTAINER = info['maintainer']
        DOWNLOAD_URL = info['download']
        GAPPS = info['gapps']
        XDA = info['forum']
        TELEGRAM = info['telegram']
        DATE_TIME = datetime.datetime.fromtimestamp(int(info['timestamp']))
        SHA256 = info['sha256']
        SIZE = round(int(info['size'])/1000000000, 2)
        msg = ""
        msg += f"DroidX-UI\n"
        msg += f"Device Name: {OEM} {DEVICE_NAME} ({DEVICE_CODENAME})\n"
        msg += f"Maintainer: {MAINTAINER}\n"
        msg += f"Date Time: {DATE_TIME}\n"
        msg += f"Download URL: {DOWNLOAD_URL}\n"
        msg += f"Size: {SIZE}G\n"
        msg += f"SHA256: {SHA256}\n"
        msg += f"GAPPS: {GAPPS}\n"
        msg += f"XDA: {XDA}\n"
        msg += f"Telegram: {TELEGRAM}\n\n"
        print(msg)
        return {
            "oem": OEM,
            "device_name": DEVICE_NAME,
            "codename": DEVICE_CODENAME,
            "maintainer": MAINTAINER,
            "datetime": DATE_TIME,
            "size": SIZE,
            "download": DOWNLOAD_URL,
            "sha256": SHA256,
            "gapps": GAPPS,
            "xda": XDA,
            "telegram": TELEGRAM
        }

# Prepare function for posting message in channel
def send_post(chat_id, image, caption, button):
    if caption == "" or not caption or caption is None:
        return bot.send_photo(chat_id=chat_id, photo=image, reply_markup=button)
    else:
        return bot.send_photo(chat_id=chat_id, photo=image, caption=caption, reply_markup=button)

# Prepare message format for channel
def message_content(information):
    msg = ""
    msg += f"<b>DroidX-UI NewHorizon // {information['oem']} {information['device_name']} ({information['codename']})</b>\n\n"
    msg += f"<b>Build Date:</b> <code>{information['datetime']} UTC</code>\n"
    msg += f"<b>Maintainer:</b> <a href='https://t.me/{information['maintainer']}'>{information['maintainer']}</a>\n"
    msg += f"<b>Screenshots:</b> <a href='https://t.me/droidxui_screenshots'>Here</a>\n"
    msg += f"<b>Support:</b> <a href='https://t.me/DroidXUI_announcements'>Channel</a> <b>|</b> <a href='https://t.me/DroidXUI_chats'>Group</a>\n"
    msg += f"\n#NewHorizon #{information['codename']} #Android14 #Official"
    return msg

# Prepare buttons for message
def button(information):
    buttons = InlineKeyboardMarkup()
    buttons.row_width = 2
    button1 = InlineKeyboardButton(text="Download", url=f"{information['download']}")
    button2 = InlineKeyboardButton(text="Installation", url=f"https://github.com/DroidX-UI-Devices/Official_Devices/blob/14/Installation/{information['codename']}.md")
    button3 = InlineKeyboardButton(text="Rom Changelogs", url=f"https://github.com/DroidX-UI/Release_changelogs/blob/14/DroidX-Changelogs.mk")
    button4 = InlineKeyboardButton(text="Release Notes", url=f"https://github.com/DroidX-UI-Devices/Official_Devices/blob/14/changelogs/{information['codename']}.md")
    button5 = InlineKeyboardButton(text="Telegram", url=f"{information['telegram']}")
    return buttons.add(button1, button2, button3, button4, button5)

# Send updates to channel and commit changes in repo
def tg_message():
    commit_message = "Update new IDs and push OTA"
    commit_description = "Data for following device(s) were changed:\n"
    if len(get_diff(get_new_id(), get_old_id())) == 0:
        print("All are Updated\nNothing to do\nExiting...")
        sleep(2)
        exit(1)
    else:
        print(f"IDs Changed:\n{get_diff(get_new_id(), get_old_id())}\n\n")
        for devices in get_diff(get_new_id(), get_old_id()):
            info = get_info(devices)
            send_post(CHAT_ID, BANNER_URL, message_content(info), button(info))
            commit_description += f"- {info['device_name']} ({info['codename']})\n"
            sleep(5)
    update(get_new_id())
    open("commit_mesg.txt", "w+").write(f"DroidX: {commit_message} [BOT]\n\n{commit_description}")


# Final stuffs
tg_message()
print("Successful")
sleep(2)
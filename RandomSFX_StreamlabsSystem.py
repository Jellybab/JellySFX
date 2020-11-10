#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# ---------------------------
#   Import Libraries
# ---------------------------
import sys
import clr
import json
import codecs
import os
import re
import random as _random
import time


sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import OBSRemoteParameters

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# ---------------------------
#   Define Global Variables
# ---------------------------

random = _random.WichmannHill()
soundfile = os.path.join(os.path.dirname(__file__), "sound.mp3")
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
UIFile = os.path.join(os.path.dirname(__file__), "UI_Config.json")
ReadMeFile = os.path.join(os.path.dirname(__file__), "ReadMe.txt")
SoundData = os.path.join(os.path.dirname(__file__), "SoundData.json")
soundsPlayed = {}
reg = None
try:
    with codecs.open(SettingsFile, encoding="utf-8-sig", mode="r") as f:
        jdata = json.load(f, encoding="utf-8")
except:
    jdata = {}
try:
    with codecs.open(SoundData, encoding="utf-8-sig", mode="r") as f:
        soundList = json.load(f, encoding="utf-8")
except:
    soundList = []

# ---------------------------
#   [Required] Script Information
# ---------------------------
ScriptName = jdata.get("ScriptName", "SFX Randomizer")
Website = "https://www.streamlabs.com"
Description = "SFX Randomizer, enables you to set up one command that can randomize between set sounds"
Creator = "Jellybab"
Version = "0.0.1"


# ---------------------------
#   [Required] Initialize Data (Only called on load)
# ---------------------------
def Init():
    global reg
    ReloadSettings(None)
    reg = re.compile(r"\$Name\([\ ]*\"(?P<name>[^\"\']+)\"[\ ]*\)")
    return


def Parse(reg, stri, x):
    global names
    result = reg.search(stri)
    if result:
        name = result.group("name")
        if names.get(name.lower(), False):
            tempx = names[name.lower()]
            tempx.append(x)
            names[name.lower()] = tempx
        else:
            names[name.lower()] = [x]


# ---------------------------------------
# Chatbot Save Settings Function
# ---------------------------------------

def ReloadSettings(jsondata):
    global jdata, WeightList, TotalWeight, Responses, names, sounds, volumes
    try:
        with codecs.open(SettingsFile, encoding="utf-8-sig", mode="r") as f:
            jsettings = json.load(f, encoding="utf-8")
    except:
        jsettings = {}

    names = {}
    reg = re.compile(r"\$Name\([\ ]*\"(?P<name>[^\"\']+)\"[\ ]*\)")

    Parent.Log("Test", str(jsettings))
    jdata = {"ScriptName": jsettings.get("ScriptName", "SFX Randomizer"),
             "SFXCommand": jsettings.get("SFXCommand", "!SFXcommand"),
             "SFXCD": jsettings.get("SFXCD", 0),
             "SoundCD": jsettings.get("SoundCD", 0),
             "SFXUserCD": jsettings.get("SFXUserCD", 0),
             "Permission": jsettings.get("Permission", "Everyone"),
             "DirPath": jsettings.get("DirPath", "PATH")}

    data = {
        "output_file": "settings.json",
        "ScriptName": {
            "type": "textbox",
            "value": jsettings.get("ScriptName", "SFX Randomizer"),
            "label": "Name of the Script/SFX",
            "tooltip": "The Name that will show in the scriptlist",
            "group": "1. This First, save settings and reload scripts after"
        },
        "SFXCommand": {
            "type": "textbox",
            "value": jsettings.get("SFXCommand", "!SFXcommand"),
            "label": "Command",
            "tooltip": "Command to activate the randomize",
            "group": "2. Command"
        },
        "SFXCD": {
            "type": "slider",
            "label": "Cooldown (min)",
            "value": jsettings.get("SFXCD", 0),
            "min": 0,
            "max": 60,
            "ticks": 1,
            "tooltip": "Time until the command can be used again",
            "group": "2. Command"
        },
        "SoundCD": {
            "type": "slider",
            "label": "sound cooldown (mins)",
            "value": jsettings.get("SoundCD", 0),
            "min": 0,
            "max": 60,
            "ticks": 1,
            "tooltip": "Time until the sound can play again",
            "group": "2. Command"
        },
        "SFXUserCD": {
            "type": "slider",
            "label": "User Cooldown (min)",
            "value": jsettings.get("SFXUserCD", 0),
            "min": 0,
            "max": 60,
            "ticks": 1,
            "tooltip": "Time until the command can be used again by the user",
            "group": "2. Command"
        },
        "Permission": {
            "type": "dropdown",
            "value": jsettings.get("Permission", "Everyone"),
            "items": ["Everyone", "Regular", "Subscriber", "Moderator"],
            "label": "Permission level",
            "tooltip": "Set the permission level for the command",
            "group": "2. Command"
        },
        "DirPath": {
            "type": "textbox",
            "value": jsettings.get("DirPath", "PATH"),
            "label": "Path to folder with SFX's",
            "tooltip": "IF Folder mode is active: put in the path to the folder with all SFX's",
            "group": "1. This First, save settings and reload scripts after"
        },
        "Open ReadMe": {
            "type": "button",
            "label": "Open ReadMe/FAQ",
            "tooltip": "Open ReadMe file",
            "function": "OpenReadMe",
            "wsevent": "EVENT_NONE"
        }
    }

    soundList = loadSongs(jsettings.get("DirPath", ""))

    with codecs.open(UIFile, encoding="utf-8-sig", mode="w") as data_file1:
        json.dump(data, data_file1, sort_keys=True, indent=4)

    with codecs.open(SettingsFile, encoding="utf-8-sig", mode="w") as data_file2:
        json.dump(jdata, data_file2, sort_keys=True, indent=4)

    with codecs.open(SoundData, encoding="utf-8-sig", mode="w") as data_file3:
        json.dump(soundList, data_file3, sort_keys=True, indent=4)


    ScriptName = jsettings.get("ScriptName", "SFX Randomizer")
    Parent.SendTwitchMessage("Loading done")
    return


# ---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
# ---------------------------
def Tick():
    return


# ---------------------------
#   [Required] Execute Data / Process messages
# ---------------------------
def Execute(data):
    global jdata
    if data.IsChatMessage() and data.GetParam(0).lower() == str(jdata["SFXCommand"]).lower():
        if Parent.HasPermission(data.User, str(jdata["Permission"]), ""):
            TryToPlaySound(data)
        else:
            Parent.SendTwitchMessage(
                data.UserName + " -> " + " You don't have permission to use " + jdata.get("A_SFXCommand",
                                                                                          "SFX Error") + " Required: " + str(
                    jdata.get("B_Permission", "Permission Error")))
    return


def TryToPlaySound(data):
    global jdata

    rnds = findRandomSong()
    now = time.localtime()
    shortnow = (now.tm_mday * 60*60*24)\
               +(now.tm_hour * 60 * 60)\
               +(now.tm_min * 60)\
               +(now.tm_sec)
    soundsPlayed[str(rnds)] = shortnow


    path = jdata.get("DirPath", "value") + str(soundList[rnds])

    if Parent.IsOnCooldown(ScriptName, jdata["ScriptName"]):
        result = Parent.GetCooldownDuration(ScriptName, jdata["ScriptName"])
        Parent.SendTwitchMessage(
            data.UserName + " -> " + jdata["ScriptName"] + " is on cooldown for " + str(result) + " seconds.")

    elif Parent.IsOnUserCooldown(ScriptName, jdata["ScriptName"], data.User):
        result = Parent.GetUserCooldownDuration(ScriptName, jdata["ScriptName"], data.User)
        Parent.SendTwitchMessage(
            data.UserName + " -> " + jdata["ScriptName"] + " is on cooldown for you for" + str(result) + " seconds.")

    else:

        if os.path.exists(path):
            playedSound = Parent.PlaySound(path, 100 / 100)

        else:
            Parent.SendTwitchMessage(
                "Warning: The path for this sound does not exist, check the spelling. Path: " + str(path))

    Parent.AddCooldown(ScriptName, jdata["ScriptName"], int(jdata["SFXCD"]) * 60)
    Parent.AddUserCooldown(ScriptName, jdata["ScriptName"], data.User, int(jdata["SFXUserCD"]) * 60)


def findRandomSong():
    notFoundSong = True

    while(notFoundSong):
        rnds = random.randint(0, len(soundList) - 1)

        if len(soundsPlayed) < len(soundList):
            if checkSongPlayed(rnds):
                notFoundSong = False
        else:
            if checkSongPlayed(rnds):
                notFoundSong = False
            else:
                Parent.SendTwitchMessage("All Songs on cooldown")
                rnds = 0
                notFoundSong = False
    return rnds


def OpenReadMe():
    """ Open the script readme file in users default .txt application. """
    os.startfile(ReadMeFile)
    return


def loadSongs(path):
    songs = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith('.mp3'):
                songs.append(filename)
    return songs


def checkSongPlayed(rnds):
    if str(rnds) in soundsPlayed:
        songTime = soundsPlayed.get(str(rnds))
        nowTime = time.localtime()
        shortnow = \
            (nowTime.tm_mday * 60*60*24)\
               +(nowTime.tm_hour * 60 * 60)\
               +(nowTime.tm_min * 60)\
               +(nowTime.tm_sec)
        songTimeInt = int(songTime)
        soundCoolDown = int(jdata.get("SoundCD")) * 60
        shortnow = int(shortnow)
        if (songTimeInt + soundCoolDown) < shortnow:
            soundsPlayed.pop(str(rnds))
            return True
        else:
            return False
    return True

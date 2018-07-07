#---------------------------
#   Import Libraries
#---------------------------
import os
import codecs
import sys
import json
import re
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#   Import your Settings class
from Settings_Module import MySettings
#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "CatchPhrases"
Website = "reecon820@gmail.com"
Description = "Allows the reaction to regular expressions whithin a chat message"
Creator = "Reecon820"
Version = "1.0.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
global SettingsFile
SettingsFile = ""
global ScriptSettings
ScriptSettings = MySettings()
global RegexDict
RegexDict = {}

global RegexPath
RegexPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "regex.conf")).replace("\\", "/")

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():

    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), "Settings")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    global SettingsFile
    SettingsFile = os.path.join(os.path.dirname(__file__), "Settings\settings.json")
    global ScriptSettings
    ScriptSettings = MySettings(SettingsFile)

    ui = {}
    UiFilePath = os.path.join(os.path.dirname(__file__), "UI_Config.json")
    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="r") as f:
            ui = json.load(f, encoding="utf-8")
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    # update ui with loaded settings
    ui['Cooldown']['value'] = ScriptSettings.Cooldown
    ui['Permission']['value'] = ScriptSettings.Permission
    ui['Info']['value'] = ScriptSettings.Info

    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="w+") as f:
            json.dump(ui, f, encoding="utf-8", indent=4, sort_keys=True)
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    LoadConfigFile()

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    #   only handle messages from chat
    if data.IsChatMessage():

        found = False
        regex = ''
        response = ''
        #   Parse chat line for the any given key word or phrase
        for rx, rp in RegexDict.iteritems():
            if re.search(rx, data.Message):
                found = True
                regex = rx
                response = rp
                break
    
        if found:
            #   Check if the command is not on cooldown and the user has permission to use the command
            if not Parent.IsOnCooldown(ScriptName, regex) and Parent.HasPermission(data.User, ScriptSettings.Permission, ScriptSettings.Info):
                Parent.BroadcastWsEvent("EVENT_MINE", "{'show':false}")
                Parent.SendStreamMessage(response)    # Send your message to chat
                Parent.AddCooldown(ScriptName, regex, ScriptSettings.Cooldown)  # Put the command on cooldown

    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    # Execute json reloading here
    ScriptSettings.Reload(jsonData)
    ScriptSettings.Save(SettingsFile)
    LoadConfigFile()
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return

def EditConfigFile():
    os.startfile(RegexPath)
    return

def LoadConfigFile():
    try:
        with codecs.open(RegexPath, encoding="utf-8-sig", mode="r") as f:
            matches = {}
            for line in f:
                regex = re.search("/.*/", line).group(0).strip('/')
                response = re.search("\".*\"", line).group(0).strip('"')
                matches[regex] = response

            global RegexDict
            RegexDict = matches

    except Exception as err:
        Parent.Log(ScriptName, "Could not load Regex file {0}".format(err))

    return
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
Version = "1.1.0.0"

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
    if data.IsChatMessage() and data.IsFromTwitch() and not data.IsWhisper():

        found = False
        regex = ''
        obj = {}
        #   Parse chat line for the any given key word or phrase
        for rx, rp in RegexDict.iteritems():
            if re.search(rx, data.Message):
                found = True
                regex = rx
                obj = rp
                break
    
        if found:
            #   Check if the command is not on cooldown and the user has permission to use the command
            if not Parent.IsOnCooldown(ScriptName, regex) and Parent.HasPermission(data.User, obj['permission'], obj['users']):
                response = Parse(obj['response'], data.User, data.Message)
                Parent.SendStreamMessage(response)    # Send your message to chat
                Parent.AddCooldown(ScriptName, regex, obj['cooldown'])  # Put the command on cooldown

    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, username, message):
    parseString = parseString.replace('$username', username)
    parseString = parseString.replace('$message', message)
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
                line = line.strip()         # remove leading and trailing spaces 
                if len(line) > 0:           # ignore empty lines
                    if line[0] != '#':      # ignore comment lines
                        tokens = list(enumerate(line.split(" ")))
                        regex = ''
                        response = ''
                        cooldown = -1
                        permission = ''
                        users = ''
                        for i, token in tokens:
                            try:
                                if re.search("^/.*/$", token):
                                    regex = re.search("^/.*/$", token).group(0).strip('/')
                                elif token[0] == '"' and not response:  
                                    # if a response is already found this token is part of the response and already handled
                                    text = ''
                                    for word in list(tokens[i:]): 
                                        text = text + " " + word[1]
                                    response = text[2:-1]
                                elif re.search("^\d$", token) and not cooldown:
                                    cooldown = int(token) if int(token) >= 0 else 0
                                elif token in ['everyone','moderator','subscriber','editor', 'user_specific'] and not permission:
                                    # if permission is already set, this token is part of the response
                                    permission = token
                                elif re.search("^(\w+,*)+$", token) and permission == 'user_specific' and not users: 
                                    # if the user list is already set, this token is part of the response
                                    users = token
                            except Exception as err:
                                Parent.Log(ScriptName, "Error while parsing line: {0} - {1}".format(line, err))

                        if not regex or not response:
                            Parent.Log(ScriptName, "Error Parsing line - no regex or response found: {}".format(line))
                            continue

                        obj = {'response': response}
                        obj['cooldown'] = cooldown if cooldown >= 0 else ScriptSettings.Cooldown
                        obj['permission'] = permission if permission else ScriptSettings.Permission
                        obj['users'] = users if users else ScriptSettings.Info

                        matches[regex] = obj 
                        
            global RegexDict
            RegexDict = matches

    except Exception as err:
        Parent.Log(ScriptName, "Could not load Regex file: {0}".format(err))

    return
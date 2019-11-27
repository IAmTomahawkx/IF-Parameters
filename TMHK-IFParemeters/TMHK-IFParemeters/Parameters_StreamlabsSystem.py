"""
The MIT License (MIT)

Copyright (c) 2019 IAmTomahawkx

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
import json
import os
import random as _random
import time
import codecs
import sys
sys.path.append(os.path.dirname(__file__))
import ArgumentParser
import scenecontrol
import view
from view import ParsingError
random = _random.WichmannHill()

# edit and die. if you want to help with this script, open a PR on github.
ScriptName = "IF parameters"
Website = None
Version = "2.0.3"
Creator = "TMHK"
Description = "fixed obs parameters"
Parent = None
filedata = os.path.join(os.path.dirname(__file__), "cache")
varfile = os.path.join(filedata, "vars.json")


variables = {}
last_save_time = time.time()
argparser = ArgumentParser.Adapter() # create my argparser instance.
controller = None # i will set this once we have the Parent at our disposal.

def send_message(message, data=None):
    """
    helper to send messages. nothing crazy.
    """
    message = message.replace("$currencyname", Parent.GetCurrencyName())
    if data:
        message = message.replace("$user", data.UserName)
        for i in range(1, data.GetParamCount()-1):
            message = message.replace("$arg"+str(i), data.GetParam(i))
    if data:
        if data.IsFromDiscord():
            Parent.SendDiscordMessage(message)
        else:
            Parent.SendStreamMessage(message)
    else:
        Parent.SendStreamMessage(message)

def intconverter(string):
    """
    helper to convert data into an integer.
    """
    try:
        return int(round(float(string.strip())))
    except:
        raise ParsingError("error while converting '{0}' to an integer".format(string))

def Init():
    """
    the setup function, this is required by the chatbot, and will be called after the Parent variable is set.
    """
    global variables
    global controller
    controller = scenecontrol.Broadcastcontrol(Parent) # set our OBS/SLOBS remote here
    if not os.path.exists(filedata): # create the directories to the cache, if they dont exist.
        os.makedirs(filedata)
    if not os.path.exists(varfile): # create the cache file itself, if it doesnt exist.
        f = open(varfile, "w")
        json.dump({'vars': {}}, f)
        f.close()
    with open(varfile) as f:
        e = f.read()
    try:
        v = json.loads(e)
        variables = v['vars']
    except:
        Parent.SendStreamMessage("IF-Error! failed to load the variable cache: file corrupt (json not readable). a new cache has been created.")
        Save()

def openreadme():
    """
    the button in the UI_Config.json file leads to this function. all it does it open the readme.
    """
    os.startfile(os.path.join(os.path.dirname(__file__), "readme.txt"))

def Execute(data):
    """
    some testing/debugging commands. i don't really expect them to be used a lot.
    """
    if not data.IsChatMessage():
        return
    if data.GetParam(0) == "!setvar" and Parent.HasPermission(data.User, "Editor", ""):
        varname = data.GetParam(1).lower()
        varvalue = " ".join(data.Message.split(" ")[2:])
        variables[varname] = varvalue
        send_message("$user, updated \"{}\" to '{}'".format(varname, varvalue), data=data)
    if data.GetParam(0) == "!getvar" and Parent.HasPermission(data.User, "Editor:"):
        varname = data.GetParam(1).lower()
        if varname in variables:
            send_message("$user, {} --> {} ".format(varname, variables[varname]), data=data)
        else:
            send_message("$user, thats not a variable!")

def Tick():
    global last_save_time
    if (time.time() - last_save_time) > 300:
        Save()
        last_save_time = time.time()
    controller.on_tick()

def Save():
    with open(varfile, "w") as f:
        json.dump({"vars": variables}, f)

def Unload():
    Save()

def readfile(filepath, randline=False):
    if not os.path.isfile(filepath):
        return "Error: Not a file"
    with open(filepath) as f:
        content = f.read()
    if randline:
        content = content.strip().split("\n")
        return random.choice(content)
    return content.replace("\n", "  ")

def writefile(arg):
    if len(arg['params']) < 2 or len(arg['params']) > 4:
        return "{{write takes a minimum of 2 argument, and a maximum of 4, not {0}}}".format(len(arg['params']))
    print(arg['params'][2:4])
    fp, data = arg['params'][0:2]
    suc, fail = "", ""
    try:
        suc, fail = arg['params'][2:4]
    except: pass
    if not os.path.isfile(fp):
        return "{writing error: File not found. does it exist?}"
    try:
        with codecs.open(fp, encoding="utf-8", mode="w") as f:
            f.write(data)
    except:
        return fail
    return suc

def parse_variables(i):
    if i['name'] == "setvar":
        variables[i['params'][0].lower()] = i['params'][1]
        return "", True
    if i['name'] in ["varPE", "varME"]:
        try:
            v = intconverter(variables[i['params'][0].lower()])
        except ParsingError:
            return "{{cannot use varPE on non-integer variable {0}}}".format(i['params'][0]), True
        except KeyError:
            v = 0
        try:
            r = intconverter(i['params'][1])
        except ParsingError as e:
            return e.message, True
        except IndexError:
            return "{{{0} takes 2 arguments, got 1}}".format(i['name']), True
        if i['name'] == "varPE":
            variables[i['params'][0].lower()] = str(int(round(v + r)))
        else:
            variables[i['params'][0].lower()] = str(int(round(v - r)))
        return "", True
    return "", False

def Parse(msg, userid, username, targetid, targetname, message):
    ret = ""
    try:
        msg = parse_arg_parameters(msg, message)
        if msg.strip() == "":
            return msg
        for i in variables:
            msg = msg.replace("<{}>".format(i), variables[i])
        if "$" not in msg:
            return msg
        args = argparser.parse(msg, 1)
        for i in args:
            if not isinstance(i, dict):
                ret += i
                continue
            a,b = parse_variables(i)
            ret += a
            del a
            if b:
                del b
                continue
            if i['name'] == "if":
                ret += parseif(i, userid, username, targetid, targetname)
            else:
                ret += i['raw']
        return ret
    except ParsingError as e:
        return e.message
    except:
        import traceback
        et, v, tb = sys.exc_info()
        with open(os.path.join(os.path.dirname(__file__), "logs.txt"), "a") as f:
            traceback.print_exception(et, v, tb, file=f)
            f.write("\n")
        return ret

def parse_arg_parameters(string, msg):
    v = view.StringView(msg)
    for index in range(1,9):
        if v.eof:
            string = string.replace("$pos"+str(index), "")
        else:
            string = string.replace("$pos"+str(index), v.get_quoted_word())
            v.skip_ws()
    return string

def parsemath(arg):
    # im hoping nothing too complex gets thrown in here
    if len(arg['params']) != 1:
        return "{{mathif takes 1 argument, not {0}}}".format(len(arg['params']))
    try:
        v = int(eval(arg['params'][0], {}, {}))
    except:
        return "{couldnt complete the math operation}"
    else:
        return str(v)

def parse_modes(var, mode, compare):
    if mode in ['==', "equals", "is"]:
        return var == compare
    if mode in ['!=', "not"]:
        return var != compare
    if mode in ['>', "greater"]:
        return intconverter(var) > intconverter(compare)
    if mode in ['<', 'smaller']:
        return intconverter(var) < intconverter(compare)
    if mode in ['<=', 'seq']:
        return intconverter(var) >= intconverter(compare)
    if mode in ['>=', 'geq']:
        return intconverter(var) <= intconverter(compare)
    if mode in ['in', '=*']:
        return var in compare
    if mode in ['notin', '!*']:
        return var not in compare
    if mode in ['permission', "haspermission"]:
        return Parent.HasPermission(var, compare, "")

def parseif(args, user, username, targetuser, targetname):
    ret = ""
    try:
        var, mode, compare, true_msg, false_msg = args['params']
    except:
        return "Not enough values passed to $if"
    tf = parse_modes(var, mode, compare)
    called_msg = true_msg if tf else false_msg
    ifargs = argparser.parse(called_msg, 1)
    for index, i in enumerate(ifargs):
        if not isinstance(i, dict):
            ret += i
            continue
        v = controller.evaluate(i)
        if isinstance(v, str):
            ret += v
            continue
        a,b = parse_variables(i)
        ret += a
        if b:
            del a,b
            continue
        if i['name'] == "if":
            ret += parseif(i, user, username, targetuser, targetname)
        if i['name'] in ["add", "remove"]:
            ret += parse_currency(i)
        if i['name'] == "getapi":
            response = json.loads(i['params'][0])
            if response['status'] != 200: # api error
                ret += response['error']
                continue
            ret += response['response']
            continue
        if i['name'] == "write":
            ret += writefile(i)
        if i['name'] == "mathif":
            ret += parsemath(i)

    return ret.strip()

def parse_currency(arg):
    success, failed = "", ""
    if len(arg['params']) < 2 or len(arg['params']) > 4:
        return "{{{0} takes a minumum of 2 arguments, and a maximum of 4, not {1}}}".format(arg['name'], len(arg['params']))
    
    userid, amount = arg['params'][0:2] # required parameters
    try:
        success, failed = arg['params'][2:4] # optional parameters
    except: pass
    amount = intconverter(amount)

    if arg['name'] == "add":
        if Parent.AddPoints(userid, Parent.GetDisplayName(userid), amount):
            return success
        return failed

    elif arg['name'] == "remove":
        if Parent.RemovePoints(userid, Parent.GetDisplayName(userid), amount):
            return success
        return failed

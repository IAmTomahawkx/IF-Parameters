___
<h1 align="center">
If Parameters
</h1>
<p align="center">
<sub>
By IAmTomahawkx<br>Version 2.2.0
</sub>
</p>

___
[![discord](https://discord.com/api/guilds/561043858402836482/embed.png)](https://discord.gg/VKp6zrs)

## What's new?
See the [full changelog](#changelog). \
This update adds in JSON parsing abilities.

___
Heads up when reading this readme!
Square brackets inside a parameter mark optional arguments. Ex. `$OBSSwapScene(scene[,delay])`. Do not actually write the square brackets!

## Custom Variables
One of the things ive always found the chatbot is lacking is ways to store your own variables without having to use \
a different file for each variable. So ive built that into this script. \
Use $setvar(variablename,value) inside or outside of $ifs. \
to use one of your variables, simply do &lt;variablename&gt; in any chatbot output (except script messages). \
this could be used to store an rpg game values, $setvar($username-health,100) etc. or how many times a certain person \
has used a certain command, $varPE($username-mycommand,1) to add one to the variable. \
$setvar(variablename,value) \
$varPE(variablename,increment) - adds the increment to the variable. only usable for numbers. \
$varME(variablename,decrement) - removes the decrement from the variable. only usable for numbers.

## Message Arguments
Ive recently heard woes over not being able to do "$if($arg1,==,,...)" to check if the user has supplied arguments in their command call. \
you can't do this because the chatbot doesn't actually run the command if it finds $arg1 in your command, but arg1 is not supplied. \
so to fix this, ive created $pos[num] parameters. they are the exact same as $arg1, $arg2 etc, but if that arg isnt given by the user, \
it simply removes the arg. so if i make an if as such; $if($pos1,==,,no parameter!,$pos1) , it will simply echo the first parameter. \
but if no first argument is given, it will tell the user "no parameter!". \
Ex. \
user: !hello there \
bot: there \
OR \
user: !hello \
bot: no parameter!

## The $if
the whole concept of this script obviously revolves around the $if.

### TL;DR
(note that the curly brackets are simply marking placeholders, they do not belong in your actual function) \
basic usage: $if({comparee},{requirement},{comparator},{true-response},{false-response}) \
as an example: $if($username,is,Tom, Hi Tom!, You're not Tom!) \
would only say "Hi Tom!" if the person who sent the message is Tom.

### The Long Version
$if takes 5 arguments, each separated by a comma (without a backslash in front of it)
the first argument is the comparee to compare against the comparator. this could be anything, as long as it follows the mode rules below.
the second argument is the mode. the mode will specify how the script should compare the two comparers. the modes and what they do are listed below
the fourth argument is the message that should be sent when the condition is met. this will be parsed only if the condition is met, and has several parameters that can go inside it.
the fifth argument is the message that should be sent when the condition is NOT met. this will only be parsed if the condition is NOT met.

## Currently Available Modes
==, equals, is - returns true when both inputs match exactly (Case Sensitive) \
\!\=, not - returns true when both inputs do not match exactly \
\>, greater - returns true when the comparee is greater than the comparator. both arguments MUST be numbers, or the operation will fail. \
\<, smaller - returns true when the comparee is smaller than the comparator. both arguments MUST be numbers, or the operation will fail. \
\>=, geq - returns true when the comparee is greater or equal to the comparator. both arguments MUST be numbers, or the operation will fail. \
\<\=, seq - returns true when the comparee is smaller or equal to the comparator. both arguments MUST be numbers, or the operation will fail. \
in, =\* - returns true if the comparee is anywhere inside the comparator. Case Sensitive. \
notin, !\* - returns true if the comparee is not anywhere inside the comparator. Case Sensitive. \
haspermission - returns true if the comparee (which must be $userid or equivalent) has the given permission. permissions are given below.

## Permissions
(these are case-sensitive)
- Follower
- Regular
- Subscriber
- VIP
- VIP+ (vips and subscribers)
- Moderator
- Editor

## Other Parameters
the following are parameters (including obs/slobs) that can go inside the true-msg and false-msg, and will be run with if.
- $setvar (see above) 
- $if (yes, they can go inside other ifs)
- $add(userid,amount) OR $add(userid,amount,succeed,fail) - adds points to the target user
- $remove(userid,amount) OR $remove(userid,amount,succeed,fail) - removes points from the user
- $getapi(url)
- $write(filepath,content) OR $write(filepath,content,succeed,fail)
- $mathif(equation)
- $balance(user) - returns info on the specified user
- $parsejson(filepath)#anchor - See [JSON Parsing](#JSON Parsing)

## OBS & SLOBS parameters
- $OBSSwapScene(scene[,delay])\
- $OBSSwapBackScene(scene1,scene2,delay)\
- $OBSSourceVisibility(source,on/off[,scene])\
- $OBSTimedSourceVisibility(source,onoff/offon,delay[,scene])

- $SLOBSSwapScene(scene[,delay])\
- $SLOBSSwapBackScene(scene,delay[,returnscene])\
- $SLOBSSourceVisibility(source,on/off[,scene])\
- $SLOBSTimedSourceVisibility(source,onoff/offon,delay[,scene])\
- $SLOBSFolderVisibility(folder,on/off[,scene])\
- $SLOBSTimedFolderVisibility(folder,on/off,delay[,scene])

## JSON Parsing
As of V2.2.0, this script now features $parsejson, which allows you to pull JSON data from a file, and grab a specific key from it.
This is a rather advanced feature, and if you don't know what this is, feel free to skip this section.
To use this, simply use the $parsejson parameter, and provide it with a filepath to a JSON file.
Afterwards, use an anchor to specify where in the json file to go.

### Anchors
Anchors are simply another way to provide arguments to the parsejson parameter. an anchor would look like this:
```
$parsejson(myfile.json)#abc
```
where `#abc` is the anchor. This allows you to navigate the JSON file in a chainable way, eg:
```
$parsejson(myfile.json)#abc.def
```
That way, when you have nested json, like this:
```json
{
  "abc": {
    "def": "ghi",
    "jkl": [
      "mno",
      "pqr"
    ]
  }
}
```
You can navigate anywhere in the file, as deep as you need to go.

You can also navigate through arrays using numbers:
```
$parsejson(myfile.json)#abc.jkl.0
```
Or you can pick a random item in the array using `!r`:
```
$parsejson(myfile.json)#abc.jkl.!r
```

___
## Contact
having problems? have questions? ideas/requests? head over to my [discord](https://discord.gg/VKp6zrs) \
I am well aware that I'm terrible at explaining things. if this readme was no help whatsoever,
feel free to jump into my discord server to ask!
You can also DM me on discord: @iamtomahawkx

___

# Changelog
2.2.0:
- Added JSON parsing ability
  - Use $parsejson for this, along with an [anchor tag](#anchors)
- Fixed a bug where the parser got too eager on argument delimiters
- Fixed a bug where the parser would sometimes remove whitespace
- Fixed a bug where the parser would remove unknown $parameters

2.1.0:
- Fixed geq `>=` and seq `<=` being treated backwards (thanks to lance lake for pointing this out)
- Added a new comparison, `indir`, which will allow you to check if a file exists in a certain directory
- Fixed backslashes (`\`) being displayed when used to escape commas

2.0.2:
- fixed haspermission not working 

2.0.1: 
- fixed some bugs 
- $pointsadd is now just $add 
- $pointsremove is now just $remove 

2.0.0: \
rewrite is here! forget everything you used to know about the $if script, its a whole new script! 
- all parameters now use normal brackets "()", and use a comma "," as a delimiter. if you want use these in your arguments,
  escape them by adding a backslash in front of them! 
- flow is a thing of the past. if you want to use multiple $ifs, put it inside your other $if!
- OBS control is here! control SLOBS and/or OBS! (do note that this may interfere with OBS/SLOBS remote parameters scripts)
- file writing is now more stable.
- ccommands have been removed. (note that this means previous ones will no longer work, sorry!)
  if you don't know what im talking about, don't worry, they're gone anyway.
- $cvar has been merged into $setvar.
- redesigned the readme (it may be moving online sometime soon™)

1.3.1: added permissions support/ file writing. \
1.3.0: SLOBS control! \
1.2.0: added built in commands for use with $args. also added currency manipulation \
1.1.0: added the ability to have multiple $if's flow into each other. changed the parameter seperator from "," to "|" \
1.0.1: added a button to open readme \
1.0.0: initial release \
with this script, you will be able to use $if parameters in your commands. but theres a bit more than that.
#!python2
import time, json, os, threading

BridgeApp = os.path.join(os.path.dirname(__file__), "bin", "SLOBSRC.exe")

class Broadcastcontrol(object):
    def __init__(self, pymanager):
        self.remote = pymanager
        self.delays = []
        self.lookup = {
            "OBSSwapScene": {"target": self.obs_scene_swap, "minargs":1},
            "OBSSwapBackScene": {"target": self.obs_scene_swap_back, "minargs":3},
            "OBSSourceVisibility": {"target": self.obs_source_visibility, "minargs":2},
            "OBSTimedSourceVisibility": {"target": self.obs_source_visibility_timed, "minargs":3},
            "SLOBSSwapScene": {"target": self.slobs_scene_swap, "minargs":1},
            "SLOBSSwapBackScene": {"target": self.slobs_scene_swap_back, "minargs":2},
            "SLOBSSourceVisibility": {"target": self.slobs_source_vis, "minargs":2},
            "SLOBSTimedSourceVisibility": {"target": self.slobs_source_vis_timed, "minargs":3},
            "SLOBSFolderVisibility": {"target": self.slobs_folder_vis, "minargs":2},
            "SLOBSTimedFolderVisibility": {"target": self.slobs_timed_folder_vis, "minargs":3}
        }
    
    def threadedexecution(self, func, *args):
        threading.Thread(target=func, args=tuple(args)).start()

    def evaluate(self, arg):
        if arg['name'] in self.lookup:
            if len(arg['params']) < self.lookup[arg['name']]['minargs']:
                return "{0} takes a minimum of {1} arguments, {2} passed".format(arg['name'], self.lookup[arg['name']]['minargs'], len(arg['params']))
            return self.lookup[arg['name']]['target'](*arg['params'])
        else:
            return arg

    def obs_logger(self, response):
        loaded = json.loads(response)
        if loaded['status'] == "error":
            self.remote.Log("$IF-OBS", loaded['error'])

    def on_tick(self):
        for i in self.delays:
            if i['time'] < time.time():
                i['action'](*i['args'])
                self.delays.remove(i)
    
    def obs_scene_swap(self, scene, delay=None):
        print(scene)
        if delay:
            self.delays.append({'time': time.time()+delay, 'action': self.remote.SetOBSCurrentScene, "args": (scene, self.obs_logger)})
            return
        self.remote.SetOBSCurrentScene(scene, self.obs_logger)
        return ""
    
    def obs_scene_swap_back(self, delay, scene_1, scene_2):
        self.remote.SetOBSCurrentScene(scene_1)
        self.delays.append({"time":time.time()+delay, "action": self.remote.SetObsCurrentScene, "args": (scene_2, self.obs_logger)})
        return ""
    
    def obs_source_visibility(self, source, onoff, scene=None):
        self.remote.SetOBSSourceRender(source, True if onoff.lower() == "on" else False, scene, self.obs_logger)
        return ""
    
    def obs_source_visibility_timed(self, source, mode, delay, scene=None):
        if mode.lower() == "onoff":
            a,b = True, False
        elif mode.lower() == "offon":
            a,b = False, True
        else:
            return "{{obs error: invalid mode: '{0}'}}".format(mode)
        self.remote.SetOBSSourceRender(source, a, scene, self.obs_logger)
        self.delays.append({"time":time.time()+delay, "action": self.remote.SetOBSSourceRender, "args": (source, b, scene)})
    
    def slobslogger(self, response):
        if response:
            self.remote.Log("$if-SLOBS", response)

    def slobs_scene_swap(self, scene, delay=None):
        def coro():
            if delay:
                self.slobslogger(os.popen("{0} change_scene \"{1}\" {2}".format(BridgeApp, scene, delay)).read())
            else:
                self.slobslogger(os.popen("{0} change_scene \"{1}\"".format(BridgeApp, scene)).read())
        self.threadedexecution(coro)
        return ""
    
    def slobs_scene_swap_back(self, scene, delay, returnscene=None):
        def coro():
            if returnscene:
                self.slobslogger(os.popen("{0} swap_scenes \"{1}\" {2} \"{3}\"".format(BridgeApp, scene, delay, returnscene)).read())
            else:
                self.slobslogger(os.popen("{0} swap_scenes \"{1}\" {2}".format(BridgeApp, scene, delay)).read())
        self.threadedexecution(coro)
        return ""
    
    def slobs_source_vis(self, source, visibility, scene=None):
        def coro():
            if scene:
                self.slobslogger(os.popen("{0} visibility_source_scene \"{1}\" \"{2}\" {3}".format(BridgeApp, source, scene, visibility)).read())
            else:
                self.slobslogger(os.popen("{0} visibility_source_active \"{1}\" {2}".format(BridgeApp, source, visibility)).read())
        self.threadedexecution(coro)
        return ""
    
    def slobs_source_vis_timed(self, source, mode, delay, scene=None):
        def coro():
            if scene:
                self.slobslogger(os.popen("{0} tvisibility_source_scene \"{1}\" \"{2}\" {3} {4}".format(BridgeApp, source, scene, delay, mode)).read())
            else:
                self.slobslogger(os.popen("{0} tvisibility_source_active \"{1}\" {2} {3}".format(BridgeApp, source, delay, mode)).read())
        self.threadedexecution(coro)
        return ""

    def slobs_folder_vis(self, folder, visibility, scene=None):
        def coro():
            if scene:
                self.slobslogger(os.popen("{0} visibility_folder_scene \"{1}\" \"{2}\" {3}".format(BridgeApp, folder, scene, visibility)).read())
            else:
                self.slobslogger(os.popen("{0} visibility_folder_active \"{1}\" {2}".format(BridgeApp, folder, visibility)).read())
        self.threadedexecution(coro)
        return ""

    def slobs_timed_folder_vis(self, folder, mode, delay, scene=None):
        def coro():
            if scene:
                self.slobslogger(os.popen("{0} tvisibility_folder_scene \"{1}\" \"{2}\" {3} {4}".format(BridgeApp, folder, scene, delay, mode)).read())
            else:
                self.slobslogger(os.popen("{0} tvisibility_folder_active \"{1}\" {2} {3}".format(BridgeApp, folder, delay, mode)).read())
        self.threadedexecution(coro)
        return ""
    
    def ThreadedFunction(self, command):
        def coro():
            self.slobslogger(os.popen("{0} {1}".format(BridgeApp, command)).read())
        self.threadedexecution(coro)

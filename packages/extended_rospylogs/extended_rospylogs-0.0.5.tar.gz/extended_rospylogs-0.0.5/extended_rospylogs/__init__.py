import sys, os
import rospy

def log_cond(cond, msg, logfunction, *args, **kwargs):
    if type(cond) != bool:
        raise TypeError("First arguemnt needs to be boolean -> Received: {}".format(type(cond)))
    if cond:
        append_name = kwargs.pop('show_name', True)
        if append_name:
            name = rospy.get_name().split("/")[-1] #get name and remove "/"
            msg = "[" + name.upper() + "] " + str(msg)
        logfunction(msg, *args, **kwargs)

def logdebug_cond(cond, msg, *args, **kwargs):
    log_cond(cond, msg, rospy.logdebug, *args, **kwargs)

def loginfo_cond(cond, msg, *args, **kwargs):
    log_cond(cond, msg, rospy.loginfo, *args, **kwargs)

def logwarn_cond(cond, msg, *args, **kwargs):
    log_cond(cond, msg, rospy.logwarn, *args, **kwargs)

def logerr_cond(cond, msg, *args, **kwargs):
    log_cond(cond, msg, rospy.logerr, *args, **kwargs)

def logfatal_cond(cond, msg, *args, **kwargs):
    log_cond(cond, msg, rospy.logfatal, *args, **kwargs)



DEBUG_LEVEL_0 = 0
DEBUG_LEVEL_1 = 1
DEBUG_LEVEL_2 = 2
DEBUG_LEVEL_3 = 3
DEBUG_LEVEL_4 = 4

log_functions = {"debug": rospy.logdebug,
               "info": rospy.loginfo,
               "warn": rospy.logwarn,
               "err": rospy.logerr,
               "fatal": rospy.logfatal}

class Debugger(object):
    debug_level = 0

    def set_debug_level(self, level):
        min_lvl = 0
        max_lvl = 4
        if (level <= max_lvl and level >= min_lvl):
            self.debug_level = level
        else:
            raise ValueError("debug_level should be between {} and {}".format(min_lvl, max_lvl))

    def debugger(self, debug_level, msg, log_type = "info", *args, **kwargs):
        if log_type in log_functions:
            log_cond(self.debug_level >= debug_level, msg,
                    log_functions[log_type], *args, **kwargs)
        else:
            raise ValueError("log_type variable should be one of these: debug, info, warn, err, fatal \n Given: {}".format(log_type))

def update_debuggers(list_debugger, debug_level):
    debug = list_debugger[0].debug_level
    if debug != debug_level:
        for debug_obj in list_debugger:
            obj_name = debug_obj.__class__.__name__
            debug_obj.debugger(DEBUG_LEVEL_0, "Updating {} to {}".format(obj_name, debug_level))
            debug_obj.set_debug_level(debug_level)

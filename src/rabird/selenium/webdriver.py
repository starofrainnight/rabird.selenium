'''
@date 2014-12-17
@author Hong-She Liang <starofrainnight@gmail.com>
'''

from selenium.common.exceptions import *
from selenium.webdriver import ChromeOptions
from selenium.webdriver import FirefoxProfile
from rabird.core.configparser import ConfigParser
from multiprocessing import Queue
from rabird.core.exceptions import *
import sys
import os
import os.path
import queue
import time
import traceback

(FEEDER_ENTER, FEEDER_EXIT) = range(0, 2)

class WatchDog(object):
    def __init__(self):
        self.__queue = Queue()
    
    def watch(self, process, timeout):
        while True:
            # Feeder enter message needs not timeout value, we just wait until an
            # enter command 
            item = self.__queue.get(True)
           
            # Command format : 
            # feeder enter : [0, formatted_stack]
            # feeder exit : [1]
            if item[0] != FEEDER_ENTER:
                continue
            
            formatted_stack = item[1]
            try:        
                item = self.__queue.get(True, timeout)
            except queue.Empty:
                process.terminate()
                raise TimeoutError(''.join(formatted_stack[:-1])) 
           
    def feeder_enter(self):
        self.__queue.put([FEEDER_ENTER, traceback.format_stack()])
    
    def feeder_exit(self):
        self.__queue.put([FEEDER_EXIT])

def switch_to_frame(self, frame):
    '''
    Added support switch to a frame where guide by the path.
    
    @param frame_path An array that contained frame ids how we could get to the
    final frame.
    '''
    if isinstance(frame, list):
        
        # First we should switch to frame window, the first element of frame 
        # path is the window's handle!
        frame_window = frame[0]
        self.switch_to_window(frame_window)
        
        frame_path = frame[1:]        
        for frame in frame_path:        
            self._old_switch_to_frame(frame)
    else:
        self._old_switch_to_frame(frame)
        
    return self
    
def force_get(self, url):
    '''
    Loads a web page in the current browser session.
    
    The differents between get() and force_get() is force_get() will stop
    the page loading process after page load timeout happened and 
    pretend the page already loaded. And force_get() will also ignored
    all popup windows that stop next page loading. 
    
    @warning: If you want this method to works as expected, you must set the 
    correct page load timeout value by set_page_load_timeout() before
    using. Otherwise, it works just like the get() and block there 
    infinite.
    '''
    try:
        # Ignore all popup windows and force to load the url. 
        self.execute_script("window.onbeforeunload = function(e){};")
        self.get(url)
    except TimeoutException as e:
        # Stop the page loading if timeout already happened.
        self.execute_script("window.stop()")
        
    return self

def get_xpath_wait_timeout(self):
    """
    Get xpath wait timeout value, default to 30 seconds
    """
    
    if "_xpath_wait_timeout" in self.__dict__:
        return self._xpath_wait_timeout
    else:
        return 30.0

def set_xpath_wait_timeout(self, timeout):
    self._xpath_wait_timeout = timeout
    
def set_watchdog(self, watchdog):
    self._watchdog = watchdog

def get_watchdog(self):
    if hasattr(self, "_watchdog"):
        return self._watchdog
    
    return None 

def get_chrome_default_profile_arguments():    
    options = ChromeOptions()
    options.add_argument("--user-data-dir=%s" % os.path.normpath(os.path.expanduser("~/.config/chromium/Default")))    
    return {"chrome_options":options}
        
def get_firefox_default_profile_arguments():
    if sys.platform == "win32":
        firefox_config_path = os.path.normpath(os.path.expandvars("$APPDATA/Mozilla/Firefox/profiles.ini"))
    else:
        firefox_config_path = os.path.normpath(os.path.expanduser("~/.mozilla/firefox/profiles.ini"))
        
    config = ConfigParser()
    config.readfp(open(firefox_config_path))
    profile_path = ""
    for section_name in config.sections():
        if not section_name.startswith("Profile"):
            continue
        
        if (config.has_option(section_name, "Default") and
            (int(config.get(section_name, "Default")) == 1)):
            if config.get(section_name, "IsRelative") == 1:
                profile_path = os.path.join(
                    os.path.dirname(firefox_config_path), 
                    config.get(section_name, "Path"))
            else:                    
                profile_path = config.get(section_name, "Path")
                
            break
         
    profile = FirefoxProfile(profile_path)
    return {"firefox_profile":profile}



'''
@date 2014-12-17
@author Hong-She Liang <starofrainnight@gmail.com>
'''

from selenium.common.exceptions import *
from selenium.webdriver import *
from rabird.core.configparser import ConfigParser
from multiprocessing import Queue
from rabird.core.exceptions import *
from six.moves import queue
from selenium.webdriver.support.ui import WebDriverWait
from . import expected_conditions as EC
import sys
import os
import os.path
import time
import traceback
import threading

class WatchDog(object):
    (FEED, STOP) = range(0, 2)
    
    def __init__(self):
        self.__queue = Queue()
        # Default timeout value set to 3 minute, if we does not have any
        # action at 3 minutes, we terminate the monitoring process
        self.__timeout = 3 * 60.0 
        
    @property
    def timeout(self):
        """Get current timeout value."""
        return self.__timeout    
    
    @timeout.setter
    def timeout(self, value):
        """Set current timeout value"""
        self.__timeout = value
        
    def _internal_daemon(self, process):
        process.join()
        
        # Force watcher exit queue waitting...
        self.feed()
        
    def watch(self, process):
        
        # Daemon thread to force watch loop exit after process exited. 
        daemon_thread = threading.Thread(target=self._internal_daemon, args=[process])
        # Set thread to daemon thread, so that we could exit this script
        # if any exceptions happended.
        daemon_thread.daemon = True
        daemon_thread.start()
        
        last_formatted_stack = [None]
        while True:
            # Process exited, we continue loop until it send STOP command 
            if not process.is_alive():
                time.sleep(3) # Wait for a while
                raise TimeoutError("Process exited without send STOP command!")
            
            try:
                # Feeder enter message needs not timeout value, we just wait until an
                # enter command 
                item = self.__queue.get(True, self.__timeout)

                if item[0] == self.STOP:
                    # Successed to stop watchdog ...
                    break
                
                # Command format : 
                # [self.FEED, formatted_stack]                
                last_formatted_stack = item[1]                
                
            except queue.Empty:
                try:
                    # Ignored all exceptions during terminate, so that 
                    # we could raise our timeout error exception. 
                    process.terminate()
                except:
                    pass
                raise TimeoutError(''.join(last_formatted_stack[:-1])) 
           
    def feed(self):
        self.__queue.put([self.FEED, traceback.format_stack()])
        
    def stop(self):
        self.__queue.put([self.STOP])

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
        self.switch_to_default_content()
        
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
        original_url = self.current_url
        for i in range(0, 3): # Try three times 
            self.execute_script("window.onbeforeunload = function(e){};")
            self.get(url)
            
            # Next code statements are just use for Chrome browser.
            # It will not ensure the url be success navigated to, so we 
            # will try 3 times until failed. 
            try:
                WebDriverWait(self, 10).until(EC.url_changed(original_url))
                break
            except TimeoutException:
                pass 
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

def execute(self, driver_command, params=None):
    '''
    All commands will pass to this function. So we just need to feed the
    watchdog here to avoid doing execution infinite here ... 
    '''
    if self.get_watchdog() is not None:
        self.get_watchdog().feed()
        
    return self._old_execute(driver_command, params)    

def if_failed_retry(self, executor, validator=lambda: False, retry_times=3, interval=1.0):
    for i in range(0, retry_times):
        try:
            result = executor()
            validated_result = validator()
            if False != validated_result:
                break            
        except Exception as e:
            traceback.print_exc()
            if i >= (retry_times - 1):
                raise # Reraise the last exception
            
        time.sleep(interval)
    return result

def get_chrome_default_arguments():    
    options = ChromeOptions()
    options.add_argument("--user-data-dir=%s" % os.path.normpath(os.path.expanduser("~/.config/chromium/Default")))    
    return {"chrome_options":options}
        
def get_firefox_default_arguments():
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

def set_recommend_preferences(self):
    # A page load behavior use 30 seconds at maximum
    self.set_page_load_timeout(30)
    self.set_window_position(0, 0)
    self.set_window_size(800, 600)
    # Command timeout value be setted to 30 seconds
    self.command_executor.set_timeout(15)
    self.set_xpath_wait_timeout(20)
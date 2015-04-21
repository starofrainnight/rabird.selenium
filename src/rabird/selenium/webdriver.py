'''
@date 2014-12-17
@author Hong-She Liang <starofrainnight@gmail.com>
'''

from selenium.common.exceptions import *

def switch_to_frame(self, frame):
    '''
    Added support switch to a frame where guide by the path.
    
    @param frame_path An array that contained frame ids how we could get to the
    final frame.
    '''
    if isinstance(frame, list):
        frame_path = frame
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

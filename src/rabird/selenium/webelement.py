


'''
@date 2014-11-16
@author Hong-She Liang <starofrainnight@gmail.com>
'''

import types
import time
import functools
import rabird.core.cstring as cstring
from . import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

def _execute_with_switch_frame(self, function):
    if  (hasattr(self, '_parent_frame_path') and 
        (len(self._parent_frame_path) > 0)):
        self._parent.switch_to_default_content()
        try:
            self._parent.switch_to_frame(self._parent_frame_path)
            result = function()
        finally:
            self._parent.switch_to_default_content()
    else:
        result = function()
    return result

def set_attribute(self, name, value):
    value = cstring.escape(value)
    script = "arguments[0].setAttribute('%s', '%s');"  % (name, value)
    function = functools.partial(self._parent.execute_script, 
                                 script, self)
    _execute_with_switch_frame(self, function)
    return self

def wait_element(self, by, value, is_existed=True, is_displayed=None, timeout=30):
    """
    Wait until the element status achieve.
    
    @param is_existed  
    @param is_displayed If is_displayed == True, that also means 
    is_existed == True. It will override the is_existed value. If 
    is_displayed == None, then this function will not care about the 
    is_displayed status.
    @param timeout If timeout equal to < 0, it will loop infinite. Otherwise 
    it will loop for timeout seconds and raise a NoSuchElementException 
    exception if can not found any element! 
    """

    # When checking is_displayed=True, that means it must exited!     
    if is_displayed:
        is_existed = True
        
    elapsed_time = 0
    element = None
    last_exception = exceptions.NoSuchElementException()
    while True:        
        try:
            element = self.find_element(by=by, value=value)
            
            # Element existed :
            
            if is_existed:
                if is_displayed is None:
                    break
                
                if element.is_displayed() == is_displayed:
                    break
                
            # If is_existed is False, that's no-means about 
            # is_displayed value.
            
        except exceptions.NoSuchElementException as e:
            last_exception = e
            
            # Element not existed :
            if not is_existed:
                # is_displayed have no means here currently! Because if 
                # is_dispalyed is True, is_existed will not False!
                #
                # And is_existed is False, that means is_dispalyed 
                # is False or None!
                break
        
        time.sleep(1)
        
        # If timeout less than 0, then this function will exit 
        # immediately. We do not allow an action execute infinite !
        elapsed_time += 1
        if elapsed_time >= timeout:
            raise last_exception
        
    return element

def xpath_find(self, *argv, **kwarg):
    return self.find_element_recursively(By.XPATH, is_find_all=False, *argv, **kwarg)[0]

def xpath_find_all(self, *argv, **kwarg):
    return self.find_element_recursively(By.XPATH, is_find_all=True, *argv, **kwarg)

def xpath_wait(self, *argv, **kwarg):
    return self.wait_element(By.XPATH, *argv, **kwarg)

def _force_hover(self):
    hover = ActionChains(self._parent).move_to_element(self)
    hover.perform()
    return self

def force_hover(self):
    function = functools.partial(_force_hover, self)
    _execute_with_switch_frame(self, function)
    return self
    
def force_focus(self):
    function = functools.partial(self._parent.execute_script, 
                                 "arguments[0].focus();", self)
    _execute_with_switch_frame(self, function)
    return self

def force_click(self):
    function = functools.partial(self._parent.execute_script, 
                                 "arguments[0].click();", self)
    _execute_with_switch_frame(self, function)
    return self

def _execute(self, command, params=None):
    function = functools.partial(self._old_execute, command, params)
    return _execute_with_switch_frame(self, function)

def _filter_elements(driver, elements, expected_conditions):
    """
    Becareful that this method will not switch to it's frame ! So you must 
    ensure you are in the correct frame currently.
    """
    result = []
    
    if (len(expected_conditions) > 0) and (len(elements) > 0):
        for element in elements:
            for condition in expected_conditions:
                if condition(element):
                    result.append(element)
    return result

def find_element_recursively(
    self, by=By.ID, value=None, parent_frame_path=[], is_find_all=False, 
    expected_conditions=[]):
    """
    Recursively to find elements ...
    
    @param expected_conditions: Only accept eecf_* functors. 
    """
    
    try:
        if isinstance(self, WebDriver):
            driver = self
        else:
            driver = self._parent
            
            # If "self" is an element and parent_frame_path do not have any 
            # elements, we should inhert the frame path from "self".
            if hasattr(self, "_parent_frame_path") and (len(parent_frame_path) <= 0):
                parent_frame_path = self._parent_frame_path
            
        last_exception = None
        founded_elements = []
        try:
            if is_find_all:
                founded_elements = self.find_elements(by, value)
            else:
                founded_elements = [self.find_element(by, value)]
                
            founded_elements = _filter_elements(driver, founded_elements, expected_conditions)                        
            for element in founded_elements:
                element._parent_frame_path = parent_frame_path
                
        except exceptions.NoSuchElementException as e:
            last_exception = e
        
        # If it only need one element ...
        if is_find_all or (len(founded_elements) <= 0):
            # You must invoke self's old find elements method, so that it could search
            # in the element not spread all over the whole HTML.
            elements = self.find_elements(By.TAG_NAME, 'iframe')
            for element in elements:
                temporary_frame_path = parent_frame_path + [element]
                driver.switch_to_default_content()
                driver.switch_to_frame(temporary_frame_path)
                try:
                    # Here must use driver to find elements, because now it already
                    # switched into the frame, so we need to search the whole frame
                    # area.
                    founded_elements += driver.find_element_recursively(
                        by, value, temporary_frame_path, is_find_all, expected_conditions)
    
                    if not is_find_all:
                        break
                except exceptions.NoSuchElementException as e:
                    last_exception = e                
        
        if (not is_find_all) and (len(founded_elements) <= 0):
            # Can't find any element, we raise the last exception if 
            # we only want to find one element !
            raise last_exception    

        return founded_elements
    
    finally:
        # Avoid stay in the specific frame after last find_element().
        driver.switch_to_default_content()

    

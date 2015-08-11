


from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.command import Command 
from selenium.webdriver.remote.webdriver import WebDriver
from . import webelement
from . import webdriver 
import types

__is_monkey_patched = False

def monkey_patch():
    global __is_monkey_patched
    
    if __is_monkey_patched:
        return

    __is_monkey_patched = True
        
    WebElement.set_attribute = types.MethodType(webelement.set_attribute, None, WebElement)
    WebElement.force_focus = types.MethodType(webelement.force_focus, None, WebElement)
    # Do not try to override the WebElement.click(), that's a different method, 
    # it will scroll to the element then click the element, if we use 
    # force_click() instead, it will take no effect on <option>. 
    WebElement.force_click = types.MethodType(webelement.force_click, None, WebElement)
    WebElement.force_hover = types.MethodType(webelement.force_hover, None, WebElement)
    
    WebElement._old_execute = WebElement._execute 
    WebElement._execute = types.MethodType(webelement._execute, None, WebElement)

    WebElement.find_element_recursively = types.MethodType(webelement.find_element_recursively, None, WebElement)
    
    WebElement.xpath_find = types.MethodType(webelement.xpath_find, None, WebElement)
    WebElement.xpath_find_all = types.MethodType(webelement.xpath_find_all, None, WebElement)
    
    WebDriver._old_switch_to_frame = WebDriver.switch_to_frame
    WebDriver.switch_to_frame = types.MethodType(webdriver.switch_to_frame, None, WebDriver)
    WebDriver.force_get = types.MethodType(webdriver.force_get, None, WebDriver)
    
    WebDriver.find_element_recursively = types.MethodType(webelement.find_element_recursively, None, WebDriver)
    
    WebDriver.xpath_find = types.MethodType(webelement.xpath_find, None, WebDriver)
    WebDriver.xpath_find_all = types.MethodType(webelement.xpath_find_all, None, WebDriver)
    
    WebDriver.is_find_element_recursively = False
    
# Try to do the monkey patch while importing this module
monkey_patch()
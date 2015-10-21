


from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.command import Command 
from selenium.webdriver.remote.webdriver import WebDriver
from . import webelement
from . import webdriver 
import types
import six

__is_monkey_patched = False

def monkey_patch():
    global __is_monkey_patched
    
    if __is_monkey_patched:
        return

    __is_monkey_patched = True
        
    WebElement.set_attribute = six.create_unbound_method(webelement.set_attribute, WebElement)
    WebElement.force_focus = six.create_unbound_method(webelement.force_focus, WebElement)
    # Do not try to override the WebElement.click(), that's a different method, 
    # it will scroll to the element then click the element, if we use 
    # force_click() instead, it will take no effect on <option>. 
    WebElement.force_click = six.create_unbound_method(webelement.force_click, WebElement)
    WebElement.force_hover = six.create_unbound_method(webelement.force_hover, WebElement)
    
    WebElement._old_execute = WebElement._execute 
    WebElement._execute = six.create_unbound_method(webelement._execute, WebElement)

    WebElement.find_element_recursively = six.create_unbound_method(webelement.find_element_recursively, WebElement)
    
    WebElement.xpath_find = six.create_unbound_method(webelement.xpath_find, WebElement)
    WebElement.xpath_find_all = six.create_unbound_method(webelement.xpath_find_all, WebElement)
    
    WebElement.xpath_wait = six.create_unbound_method(webelement.xpath_wait, WebElement)
    WebElement.xpath_wait_all = six.create_unbound_method(webelement.xpath_wait_all, WebElement)
    
    WebDriver._old_switch_to_frame = WebDriver.switch_to_frame
    WebDriver.switch_to_frame = six.create_unbound_method(webdriver.switch_to_frame, WebDriver)
    WebDriver.force_get = six.create_unbound_method(webdriver.force_get, WebDriver)
    
    WebDriver.find_element_recursively = six.create_unbound_method(webelement.find_element_recursively, WebDriver)
    
    WebDriver.xpath_find = six.create_unbound_method(webelement.xpath_find, WebDriver)
    WebDriver.xpath_find_all = six.create_unbound_method(webelement.xpath_find_all, WebDriver)
    
    WebDriver.xpath_wait = six.create_unbound_method(webelement.xpath_wait, WebDriver)
    WebDriver.xpath_wait_all = six.create_unbound_method(webelement.xpath_wait_all, WebDriver)
        
    WebDriver.get_xpath_wait_timeout = six.create_unbound_method(webdriver.get_xpath_wait_timeout, WebDriver)
    WebDriver.set_xpath_wait_timeout = six.create_unbound_method(webdriver.set_xpath_wait_timeout, WebDriver)
    
    WebDriver.set_watchdog = six.create_unbound_method(webdriver.set_watchdog, WebDriver)
    WebDriver.get_watchdog = six.create_unbound_method(webdriver.get_watchdog, WebDriver)
    
    WebDriver._old_execute = WebDriver.execute 
    WebDriver.execute = six.create_unbound_method(webdriver.execute, WebDriver)
        
# Try to do the monkey patch while importing this module
monkey_patch()
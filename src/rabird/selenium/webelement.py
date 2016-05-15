


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
from selenium.webdriver.support.ui import WebDriverWait
from rabird.selenium import expected_conditions as EC

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

def __get_driver(self):
    if isinstance(self, WebDriver):
        driver = self
    else:
        driver = self._parent

    return driver

def xpath_find(self, *args, **kwargs):
    return self.find_element_recursively(By.XPATH, *args, is_find_all=False, **kwargs)[0]

def xpath_find_all(self, *args, **kwargs):
    return self.find_element_recursively(By.XPATH, *args, is_find_all=True, **kwargs)

def xpath_wait(self, *args, **kwargs):
    """
    A simple method provided for wait specific xpath expression appear.
    """

    if "timeout" in kwargs:
        timeout = kwargs["timeout"]
    else:
        timeout = __get_driver(self).get_xpath_wait_timeout()

    if "value" in kwargs:
        value = kwargs["value"]
    else:
        value = args[0]

    return WebDriverWait(__get_driver(self), timeout).until(
        EC.xpath_find(value))

def xpath_wait_all(self, *args, **kwargs):
    if "timeout" in kwargs:
        timeout = kwargs["timeout"]
    else:
        timeout = __get_driver(self).get_xpath_wait_timeout()

    if "value" in kwargs:
        value = kwargs["value"]
    else:
        value = args[0]

    return WebDriverWait(__get_driver(self), timeout).until(
        EC.xpath_find_all(value))

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

def _filter_elements(driver, elements, conditions):
    """
    Becareful that this method will not switch to it's frame ! So you must
    ensure you are in the correct frame currently.
    """
    result = []

    if (len(conditions) > 0) and (len(elements) > 0):
        for element in elements:
            for condition in conditions:
                if condition(element):
                    result.append(element)
    else:
        result = elements

    return result

def __find_element_recursively(
    self, by=By.ID, value=None, conditions=[], is_find_all=False, parent_frame_path=[]):
    """
    Recursively to find elements ...

    @param conditions: Only accept eecf_* functors.
    @return Return element list while successed, otherwise raise exception
    NoSuchElementException .
    """

    if isinstance(self, WebDriver):
        driver = self
    else:
        driver = self._parent

        # If "self" is an element and parent_frame_path do not have any
        # elements, we should inhert the frame path from "self".
        if hasattr(self, "_parent_frame_path") and (len(parent_frame_path) <= 0):
            parent_frame_path = self._parent_frame_path

    # Initialize first frame path to current window handle
    if len(parent_frame_path) <= 0:
        parent_frame_path += [driver.current_window_handle]
    else:
        # FIXME I don't know why, but it can find the iframe even
        # we switched into that iframe??? Seems that switch behavior
        # failed!
        iframe_elements = self.find_elements(By.TAG_NAME, 'iframe')
        if parent_frame_path[-1] in iframe_elements:
            raise exceptions.NoSuchElementException()

    try:
        last_exception = exceptions.NoSuchElementException("by: %s, value: %s" % (by, value))
        founded_elements = []
        try:
            if is_find_all:
                founded_elements = self.find_elements(by, value)
            else:
                founded_elements = [self.find_element(by, value)]

            founded_elements = _filter_elements(driver, founded_elements, conditions)
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
                driver.switch_to_frame(temporary_frame_path)

                try:
                    # Here must use driver to find elements, because now it already
                    # switched into the frame, so we need to search the whole frame
                    # area.
                    founded_elements += __find_element_recursively(self,
                        by, value, conditions, is_find_all, temporary_frame_path)

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


def __has_visible_condition(conditions):
    for condition in conditions:
        if not isinstance(condition, EC.eecf_operator):
            if isinstance(condition, EC.eecf_visible_of):
                return True

            continue

        if __has_visible_condition(condition):
            return True

def find_element_recursively(self, *args, **kwargs):
    if isinstance(self, WebDriver):
        driver = self
    else:
        driver = self._parent

    conditions = []
    if 'conditions' in kwargs:
        conditions = kwargs["conditions"]
    elif len(args) >= 3:
        conditions = args[2]

    if not __has_visible_condition(conditions):
        # By default, we only check visible elements
        # Think about it, most behaviors are done on visible elements not
        # the hiden elements !
        conditions.append(EC.eecf_visible())
    kwargs["conditions"] = conditions

    founded_elements = []

    # Recursive into windows
    old_handle = driver.current_window_handle
    try:
        handles = driver.window_handles
        for handle in handles:
            driver.switch_to_window(handle)
            founded_elements += __find_element_recursively(self, *args, **kwargs)
            if (not kwargs["is_find_all"]) and (len(founded_elements) > 0):
                break
    finally:
        driver.switch_to_window(old_handle)

    return founded_elements

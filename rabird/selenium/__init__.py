# -*- coding: utf-8 -*-

"""Top-level package for rabird.selenium."""

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.switch_to import SwitchTo
from .overrides import webelement
from .overrides import webdriver
from .overrides import switch_to
import types
import six

__author__ = """Hong-She Liang"""
__email__ = "starofrainnight@gmail.com"
__version__ = "0.12.5"

__is_monkey_patched = False


def monkey_patch():
    global __is_monkey_patched

    if __is_monkey_patched:
        return

    __is_monkey_patched = True

    WebElement._old_get_attribute = WebElement.get_attribute
    WebElement.get_attribute = six.create_unbound_method(
        webelement.get_attribute, WebElement
    )
    WebElement.set_attribute = six.create_unbound_method(
        webelement.set_attribute, WebElement
    )
    WebElement.force_focus = six.create_unbound_method(
        webelement.force_focus, WebElement
    )
    # Do not try to override the WebElement.click(), that's a different method,
    # it will scroll to the element then click the element, if we use
    # force_click() instead, it will take no effect on <option>.
    WebElement.force_click = six.create_unbound_method(
        webelement.force_click, WebElement
    )
    WebElement.force_hover = six.create_unbound_method(
        webelement.force_hover, WebElement
    )

    WebElement.scroll_into_view = six.create_unbound_method(
        webelement.scroll_into_view, WebElement
    )

    WebElement._old_execute = WebElement._execute
    WebElement._execute = six.create_unbound_method(
        webelement._execute, WebElement
    )

    WebElement.find_element_recursively = six.create_unbound_method(
        webelement.find_element_recursively, WebElement
    )

    WebElement.xpath_find = six.create_unbound_method(
        webelement.xpath_find, WebElement
    )
    WebElement.xpath_find_all = six.create_unbound_method(
        webelement.xpath_find_all, WebElement
    )

    WebElement.xpath_wait = six.create_unbound_method(
        webelement.xpath_wait, WebElement
    )
    WebElement.xpath_wait_all = six.create_unbound_method(
        webelement.xpath_wait_all, WebElement
    )

    WebElement.remove = six.create_unbound_method(
        webelement.remove, WebElement
    )

    # Fixed property 'rect' not working in most webdriver, we emulated one.
    WebElement._old_rect = WebElement.rect
    WebElement.rect = property(
        six.create_unbound_method(webelement.get_rect, WebElement)
    )

    WebElement.absolute_location = property(
        six.create_unbound_method(webelement.get_absolute_location, WebElement)
    )

    # Fixed 'screenshot_as_xxx()' not working in most webdriver, we emulated
    # one.
    # Seems screenshot_as_xxx() works now try to enable it --- 2019-02-12
    # WebElement._old_screenshot_as_base64 = WebElement.screenshot_as_base64
    # WebElement.screenshot_as_base64 = property(
    #     six.create_unbound_method(webelement.screenshot_as_base64, WebElement))

    SwitchTo._old_frame = SwitchTo.frame
    SwitchTo.frame = six.create_unbound_method(switch_to.frame, SwitchTo)

    WebDriver.force_get = six.create_unbound_method(
        webdriver.force_get, WebDriver
    )

    WebDriver.open_window = six.create_unbound_method(
        webdriver.open_window, WebDriver
    )
    WebDriver.close_window = six.create_unbound_method(
        webdriver.close_window, WebDriver
    )

    WebDriver.find_element_recursively = six.create_unbound_method(
        webelement.find_element_recursively, WebDriver
    )

    WebDriver.xpath_find = six.create_unbound_method(
        webelement.xpath_find, WebDriver
    )
    WebDriver.xpath_find_all = six.create_unbound_method(
        webelement.xpath_find_all, WebDriver
    )

    WebDriver.xpath_wait = six.create_unbound_method(
        webelement.xpath_wait, WebDriver
    )
    WebDriver.xpath_wait_all = six.create_unbound_method(
        webelement.xpath_wait_all, WebDriver
    )

    WebDriver.set_timeouts_safety = six.create_unbound_method(
        webdriver.set_timeouts_safety, WebDriver
    )

    WebDriver.get_xpath_wait_timeout = six.create_unbound_method(
        webdriver.get_xpath_wait_timeout, WebDriver
    )
    WebDriver.set_xpath_wait_timeout = six.create_unbound_method(
        webdriver.set_xpath_wait_timeout, WebDriver
    )

    WebDriver.set_watchdog = six.create_unbound_method(
        webdriver.set_watchdog, WebDriver
    )
    WebDriver.get_watchdog = six.create_unbound_method(
        webdriver.get_watchdog, WebDriver
    )
    WebDriver.get_pid = six.create_unbound_method(webdriver.get_pid, WebDriver)
    WebDriver._restart_connection = six.create_unbound_method(
        webdriver._restart_connection, WebDriver
    )

    WebDriver._old_execute = WebDriver.execute
    WebDriver.execute = six.create_unbound_method(webdriver.execute, WebDriver)


# Try to do the monkey patch while importing this module
monkey_patch()

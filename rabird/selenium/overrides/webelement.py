"""
@date 2014-11-16
@author Hong-She Liang <starofrainnight@gmail.com>
"""

import io
import types
import time
import functools
import base64
import copy
import rabird.core.cstring as cstring
from PIL import Image
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException,
    NoSuchFrameException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from rabird.selenium import expected_conditions as EC
from rabird.selenium import validators as V
from ..utils import merge_kwargs, verify_xpath, get_current_func


def _execute_with_switch_frame(self, function):
    if hasattr(self, "_parent_frame_path") and (
        len(self._parent_frame_path) > 0
    ):
        self._parent.switch_to.default_content()
        try:
            self._parent.switch_to.frame(self._parent_frame_path)
            # Try to scroll element to view before execute any function
            _do_scroll_into_view(self)
            result = function()
        finally:
            self._parent.switch_to.default_content()
    else:
        # Try to scroll element to view before execute any function
        _do_scroll_into_view(self)
        result = function()
    return result


def get_attribute(self, name):
    function = functools.partial(self._old_get_attribute, name)
    return _execute_with_switch_frame(self, function)


def set_attribute(self, name, value):
    value = cstring.escape(value)
    script = "arguments[0].setAttribute('%s', '%s');" % (name, value)
    function = functools.partial(self._parent.execute_script, script, self)
    _execute_with_switch_frame(self, function)
    return self


def __get_driver(self):
    if isinstance(self, WebDriver):
        driver = self
    else:
        driver = self._parent

    return driver


def _xpath_find_decl(
    value=None,
    validators=None,
    is_find_all=False,
    parent_frame_path=None,
    **kwargs
):
    """Only xpath parameters declaration of xpath_find related function.
    """

    pass


def xpath_find(self, *args, **kwargs):
    return self.find_element_recursively(
        By.XPATH, *args, is_find_all=False, **kwargs
    )[0]


def xpath_find_all(self, *args, **kwargs):
    return self.find_element_recursively(
        By.XPATH, *args, is_find_all=True, **kwargs
    )


def xpath_wait(self, *args, **kwargs):
    """
    A simple method provided for wait specific xpath expression appear.
    """

    if "timeout" in kwargs:
        timeout = kwargs["timeout"]
        del kwargs["timeout"]
    else:
        timeout = __get_driver(self).get_xpath_wait_timeout()

    # Because WebDriverWait() will ignore all exceptions even
    # InvalidSelectorException, so we will check xpath pattern if valid first.
    # If xpath pattern verify failed, we must not go into looping and report
    # to user.
    merged_kwargs = merge_kwargs(_xpath_find_decl, args, kwargs)
    verify_xpath(merged_kwargs["value"])

    return WebDriverWait(__get_driver(self), timeout).until(
        EC.xpath_find(*args, **kwargs)
    )


def xpath_wait_all(self, *args, **kwargs):
    if "timeout" in kwargs:
        timeout = kwargs["timeout"]
        del kwargs["timeout"]
    else:
        timeout = __get_driver(self).get_xpath_wait_timeout()

    # Because WebDriverWait() will ignore all exceptions even
    # InvalidSelectorException, so we will check xpath pattern if valid first.
    # If xpath pattern verify failed, we must not go into looping and report
    # to user.
    merged_kwargs = merge_kwargs(_xpath_find_decl, args, kwargs)
    verify_xpath(merged_kwargs["value"])

    return WebDriverWait(__get_driver(self), timeout).until(
        EC.xpath_find_all(*args, **kwargs)
    )


def _force_hover(self):
    hover = ActionChains(self._parent).move_to_element(self)
    hover.perform()
    return self


def force_hover(self):
    function = functools.partial(_force_hover, self)
    _execute_with_switch_frame(self, function)
    return self


def force_focus(self):
    function = functools.partial(
        self._parent.execute_script, "arguments[0].focus();", self
    )
    _execute_with_switch_frame(self, function)
    return self


def force_click(self):
    function = functools.partial(
        self._parent.execute_script, "arguments[0].click();", self
    )
    _execute_with_switch_frame(self, function)
    return self


def _do_scroll_into_view(self):
    self._parent.execute_script("arguments[0].scrollIntoView(true);", self)


def scroll_into_view(self):
    function = functools.partial(_do_scroll_into_view, self)
    _execute_with_switch_frame(self, function)
    return self


def _execute(self, command, params=None):
    function = functools.partial(self._old_execute, command, params)
    return _execute_with_switch_frame(self, function)


def _filter_elements(driver, elements, validators):
    """Becareful that this method will not switch to it's frame ! So you must
    ensure you are in the correct frame currently.
    """
    # Only filter elements if validators not empty!
    if (
        (validators is None)
        or (isinstance(validators, list) and (len(validators) <= 0))
        or (not elements)
    ):
        return elements

    result = []

    # Only do filter behavior if
    for element in elements:
        for validator in validators:
            if validator(element):
                result.append(element)

    return result


def _find_element_recursively(
    self,
    by=By.ID,
    value=None,
    validators=None,
    is_find_all=False,
    parent_frame_path=None,
    **kwargs
):
    """Recursively to find elements.

    @param validators: Only accept validators.
    @return Return element list while successed, otherwise raise exception
    NoSuchElementException .
    """
    if parent_frame_path is None:
        parent_frame_path = list()

    if validators is None:
        validators = V.And()
    elif not isinstance(validators, V.Operator):
        validators = V.And(*validators)

    if isinstance(self, WebDriver):
        driver = self
    else:
        driver = self._parent

        # If "self" is an element and parent_frame_path do not have any
        # elements, we should inhert the frame path from "self".
        if hasattr(self, "_parent_frame_path") and (
            len(parent_frame_path) <= 0
        ):
            parent_frame_path = self._parent_frame_path

    # Initialize first frame path to current window handle
    if len(parent_frame_path) <= 0:
        parent_frame_path += [driver.current_window_handle]
    else:
        # FIXME I don't know why, but it can find the iframe even
        # we switched into that iframe??? Seems that switch behavior
        # failed!
        iframe_elements = self.find_elements(By.TAG_NAME, "iframe")
        if parent_frame_path[-1] in iframe_elements:
            raise NoSuchElementException()

    try:
        last_exception = NoSuchElementException(
            "by: %s, value: %s" % (by, value)
        )
        founded_elements = []
        try:
            if is_find_all:
                founded_elements = self.find_elements(by, value)
            else:
                founded_elements = [self.find_element(by, value)]

            founded_elements = _filter_elements(
                driver, founded_elements, validators
            )
            for element in founded_elements:
                element._parent_frame_path = parent_frame_path

        except NoSuchElementException as e:
            last_exception = e

        # If it only need one element ...
        if is_find_all or (len(founded_elements) <= 0):
            # You must invoke self's old find elements method, so that it could search
            # in the element not spread all over the whole HTML.
            try:
                elements = []
                elements = self.find_elements(By.TAG_NAME, "iframe")
            except WebDriverException:
                # If window is switching or not ready, WebDriverException will
                # happen.
                pass

            for element in elements:
                try:
                    temporary_frame_path = parent_frame_path + [element]
                    driver.switch_to.frame(temporary_frame_path)

                    try:
                        # Here must use driver to find elements, because now it already
                        # switched into the frame, so we need to search the whole frame
                        # area.
                        founded_elements += _find_element_recursively(
                            self,
                            by,
                            value,
                            validators,
                            is_find_all,
                            temporary_frame_path,
                            **kwargs
                        )

                        if not is_find_all:
                            break
                    except NoSuchElementException as e:
                        last_exception = e
                except (
                    StaleElementReferenceException,
                    NoSuchFrameException,
                ) as e:
                    # Sometimes, we will met staled or none iframe event found
                    # the 'iframe' element before.
                    print(
                        "Can't find stale iframe : %s! Current Window Handle : %s"
                        % (temporary_frame_path, driver.current_window_handle)
                    )
                    last_exception = e

        if (not is_find_all) and (len(founded_elements) <= 0):
            # Can't find any element, we raise the last exception if
            # we only want to find one element !
            raise last_exception

        return founded_elements

    finally:
        # Avoid stay in the specific frame after last find_element().
        driver.switch_to.default_content()


def _has_visible_validator(validators):
    for validator in validators:
        if not isinstance(validator, V.Operator):
            if isinstance(validator, V.VisibleOf):
                return True

            continue

        if _has_visible_validator(validator):
            return True

    return False


def find_element_recursively(
    self,
    by=By.ID,
    value=None,
    validators=[],
    is_find_all=False,
    *args,
    **kwargs
):
    if isinstance(self, WebDriver):
        driver = self
    else:
        driver = self._parent

    if not _has_visible_validator(validators):
        # By default, we only check visible elements
        # Think about it, most behaviors are done on visible elements not
        # the hiden elements !
        validators.append(V.Visible())

    founded_elements = []

    # Recursive into windows
    last_exception = NoSuchElementException()
    old_handle = driver.current_window_handle
    try:
        handles = driver.window_handles
        for handle in handles:
            driver.switch_to.window(handle)
            try:
                founded_elements += _find_element_recursively(
                    self, by, value, validators, is_find_all, *args, **kwargs
                )
                if (not is_find_all) and (len(founded_elements) > 0):
                    break
            except NoSuchElementException as e:
                # Continue searching if there does not have element in specific
                # window.
                last_exception = e
    finally:
        driver.switch_to.window(old_handle)

    if (len(founded_elements) <= 0) and (not is_find_all):
        # If no one have any elements, we should raise last exception (There
        # must be someone raised that exception!)
        raise last_exception

    return founded_elements


def remove(self):
    script = """
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """

    function = functools.partial(self._parent.execute_script, script, self)
    _execute_with_switch_frame(self, function)


def get_rect(self):
    """
    Emulated rect property for all webdriver.

    Original method will raise unknow command exception in most webdrivers.
    """

    rect = copy.deepcopy(self.location)
    rect.update(self.size)
    return rect


def get_absolute_location(self):
    """
    Get element's location relate to the whole web page

    Original location property only get the location related to frame which
    containing it.
    """

    location = self.location

    if hasattr(self, "_parent_frame_path") and (
        len(self._parent_frame_path) > 0
    ):
        last_frame = self._parent_frame_path[-1]
        frame_list = self._parent_frame_path[:-1]

        # Sum up parent frames' locations (frame's location also related to
        # which frame containing it.)

        count = len(frame_list)
        for i in range(count, 0, -1):
            self.parent.switch_to.frame(frame_list[:i])
            frame_location = last_frame.location

            location["x"] += frame_location["x"]
            location["y"] += frame_location["y"]

            last_frame = frame_list[-1]

    return location


def screenshot_as_base64(self):
    """
    An emulated element screenshot method.

    Original screenshot_as_base64() and screenshot_as_png() is new features that
    not be supported by most webdrivers. So we provided a complicated way to
    achieve the same goal with same interface. Hope it will support all
    webdrivers.
    """

    self.scroll_into_view()
    image_data = self.parent.get_screenshot_as_png()

    location = get_absolute_location(self)

    # Compatible way to get scroll x and y.
    # Reference to :
    # https://developer.mozilla.org/en-US/docs/Web/API/Window/scrollX
    scroll_x = self.parent.execute_script(
        "return (window.pageXOffset !== undefined) ? window.pageXOffset : ("
        "document.documentElement || "
        "document.body.parentNode || "
        "document.body).scrollLeft;"
    )
    scroll_y = self.parent.execute_script(
        "return (window.pageYOffset !== undefined) ? window.pageYOffset : ("
        "document.documentElement || "
        "document.body.parentNode || "
        "document.body).scrollTop;"
    )

    size = self.size

    image = Image.open(io.BytesIO(image_data))

    left = location["x"] - scroll_x
    # FIXME: Why subtract with 150? No, don't ask me, it just works!
    top = location["y"] - scroll_y - 150
    right = left + size["width"]
    bottom = top + size["height"]

    stream = io.BytesIO()
    image = image.crop((int(left), int(top), int(right), int(bottom)))
    image.save(stream, format="PNG")

    return base64.b64encode(stream.getvalue()).decode("ascii")

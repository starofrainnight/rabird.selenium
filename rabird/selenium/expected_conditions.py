"""
Provide a series Element Expected Condition Functors

@date 2015-08-03
@author Hong-She Liang <starofrainnight@gmail.com>
"""

# Import all expected conditions from selenium
from selenium.webdriver.support.expected_conditions import *
import re
import six
import warnings


class C(dict):
    """
    Simple condition wrapper class to help simplify coding of match
    conditions.
    """

    def __init__(self, condition, **kwargs):
        kwargs.setdefault("required", True)
        kwargs["condition"] = condition

        self.clear()
        self.update(kwargs)


class match(object):
    """
    Use for wait a series conditions and return their result to a list.

    @code
    checkcode, password = WebDriverWait(driver, 10).until(EC.match(
        EC.C(EC.xpath("//input[@id='fm-login-checkcode']")),
        EC.C(EC.xpath("//input[@id='fm-login-password']")),
    ))
    checkcode.clear()
    @endcode
    """

    def __init__(self, *args, **kwargs):
        self._conditions = args
        self._at_least = kwargs.get("matched_at_least", 1)

    def __call__(self, driver):
        elements = []

        matched_count = 0
        for i in range(0, len(self._conditions)):
            v = self._conditions[i]
            elements.append(None)

            value = v["condition"](driver)
            if False != value:
                elements[i] = value
                matched_count += 1
            elif v["required"]:
                # If required flag is True and value is False, we return False
                return False

        if matched_count < self._at_least:
            return False

        return elements


class xpath(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def __call__(self, driver):
        try:
            return driver.xpath_find(*self._args, **self._kwargs)
        except NoSuchElementException:
            # Because wait method will invoke xpath_find() multi-times,
            # can't find the element is a normal state, so we must not
            # scare.
            return False
        except WebDriverException as e:
            if "element is not attached to the page document" in str(e):
                return False

            raise


class xpath_find(xpath):
    def __init__(self, *args, **kwargs):
        warnings.warn("use 'xpath' instead", DeprecationWarning)

        super().__init__(*args, **kwargs)


class xpath_all(object):
    """
    Easily to wait until find all elements recursively.

    Example :

    @code
    elements = WebDriverWait(driver, 10).until(EC.xpath_all(
        "//input[@id='fm-login-id']",
        validators=[validators.VisibleOf(True)]))
    @endcode
    """

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def __call__(self, driver):
        elements = driver.xpath_find_all(*self._args, **self._kwargs)
        if len(elements) > 0:
            return elements
        else:
            return False


class xpath_find_all(xpath_all):
    def __init__(self, *args, **kwargs):
        warnings.warn("use 'xpath_all' instead", DeprecationWarning)

        super().__init__(*args, **kwargs)


class xpath_not_existed(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def __call__(self, driver):
        try:
            driver.xpath_find(*self._args, **self._kwargs)
            return False
        except NoSuchElementException:
            return True
        except WebDriverException as e:
            if "element is not attached to the page document" in str(e):
                return False

            raise


class url_changed(object):
    """
    Wait until webdriver's current url changed

    @param url: Original webdriver's current url, normally you should
    pass the webdriver.current_url.
    """

    def __init__(self, url):
        self._url = url

    def __call__(self, driver):
        return driver.current_url != self._url


class url_changed_to(object):
    """
    Wait until webdriver's current url changed to specific url

    @param regex_object: The target url should be match to this regex!
    """

    def __init__(self, regex_object):
        self._regex_object = regex_object

    def __call__(self, driver):
        if isinstance(self._regex_object, six.string_types):
            return self._regex_object == driver.current_url
        else:
            return self._regex_object.match(driver.current_url) is not None

'''
Provide a series Element Expected Condition Functors

@date 2015-08-03
@author Hong-She Liang <starofrainnight@gmail.com>
'''

# Import all expected conditions from selenium 
from selenium.webdriver.support.expected_conditions import *

class eecf_stale_of(object):
    def __init__(self, check_status):
        self.__check_status = check_status
    
    def __call__(self, element):
        try:
            # Calling any method forces a staleness check
            element.is_enabled()
            return self.__check_status 
        except StaleElementReferenceException:
            return not self.__check_status 
                    
class eecf_visible_of(object):
    def __init__(self, check_status):
        self.__check_status = check_status
    
    def __call__(self, element):    
        try:
            return element.is_displayed() == self.__check_status
        except (NoSuchElementException, StaleElementReferenceException):
            # In the case of NoSuchElement, returns true because the element is
            # not present in DOM. The try block checks if the element is present
            # but is invisible.
            # In the case of StaleElementReference, returns true because stale
            # element reference implies that element is no longer visible.
            return not self.__check_status 
    
class eecf_select_of(object):
    def __init__(self, check_status):
        self.__check_status = check_status
        
    def __call__(self, element):
        return element.is_selected() == self.__check_status
       
class eecf_enable_of(object):
    def __init__(self, check_status):
        self.__check_status = check_status
        
    def __call__(self, element):
        """ Wait until an element is enabled
        returns False otherwise.
        """
        # Calling any method forces a staleness check
        return element.is_enabled() == self.__check_status
        
class xpath_find(object):
    def __init__(self, xpath_expr, expected_conditions=[]):
        self.__xpath_expr = xpath_expr
        self.__expected_conditions = expected_conditions

    def __call__(self, driver):
        elements = driver.xpath_find(self.__xpath_expr, 
            expected_conditions=self.__expected_conditions)
        if len(elements) > 0:
            return elements
        else:
            return False
        
class xpath_find_all(object):
    """
    Easily to wait until find all elements recursively.
    
    Example : 
    
    @code
    elements = WebDriverWait(driver, 10).until(EC.xpath_find(
        "//input[@id='fm-login-id']",
        expected_conditions=[eecf_visible_of(True)]))
    @endcode 
    """
    def __init__(self, xpath_expr, expected_conditions=[]):
        self.__xpath_expr = xpath_expr
        self.__expected_conditions = expected_conditions

    def __call__(self, driver):
        elements = driver.xpath_find_all(self.__xpath_expr, 
            expected_conditions=self.__expected_conditions)
        if len(elements) > 0:
            return elements
        else:
            return False
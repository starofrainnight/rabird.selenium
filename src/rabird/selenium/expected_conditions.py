'''
Provide a series Element Expected Condition Functors

@date 2015-08-03
@author Hong-She Liang <starofrainnight@gmail.com>
'''

# Import all expected conditions from selenium 
from selenium.webdriver.support.expected_conditions import *
import re

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
        
class eecf_stale(eecf_stale_of):
    def __init__(self):
        super().__init__(True)
        
class eecf_fresh(eecf_stale_of):
    def __init__(self):
        super().__init__(False)
                    
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
        
class eecf_visible(eecf_visible_of):
    def __init__(self):
        super().__init__(True)
        
class eecf_invisible(eecf_visible_of):
    def __init__(self):
        super().__init__(False)

class eecf_existed(object):
    """
    This condition only use to check if element existed, don't care if 
    it visible or not.
    """
    
    def __init__(self):
        pass
    
    def __call__(self, element):
        return element is not None
    
class eecf_select_of(object):
    def __init__(self, check_status):
        self.__check_status = check_status
        
    def __call__(self, element):
        return element.is_selected() == self.__check_status
    
class eecf_selected(eecf_select_of):
    def __init__(self):
        super().__init__(True)
        
class eecf_deselected(eecf_select_of):
    def __init__(self):
        super().__init__(False)
       
class eecf_enable_of(object):
    def __init__(self, check_status):
        self.__check_status = check_status
        
    def __call__(self, element):
        """ Wait until an element is enabled
        returns False otherwise.
        """
        # Calling any method forces a staleness check
        return element.is_enabled() == self.__check_status
    
class eecf_enabled(eecf_enable_of):
    def __init__(self):
        super().__init__(True)
        
class eecf_disabled(eecf_enable_of):
    def __init__(self):
        super().__init__(False)
        
class eecf_operator(list):
    pass
    
class eecf_and(eecf_operator):
    def __init__(self, *args):
        super().__init__(args)
    
    def __call__(self, element):
        for condition in self:
            if not condition(element):
                return False
                
        return True
    
class eecf_or(eecf_operator):
    def __init__(self, *args):
        super().__init__(args)
    
    def __call__(self, element):
        for condition in self:
            if condition(element):
                return True
                
        return False
    
class eecf_not(eecf_operator):
    def __init__(self, condition):
        super().__init__([condition])
    
    def __call__(self, element):
        return not self[0](element)
    
class C(dict):
    """
    Simple condition wrapper class to help simplify coding of match 
    conditions.
    """
    
    def __init__(self, condition, **kwargs):
        # Support "optional" option only for backward compatible.
        if "optional" not in kwargs:
            kwargs["optional"] = False
            
        kwargs["required"] = not kwargs["optional"]            
        kwargs["condition"] = condition
        
        self.clear()
        self.update(kwargs)        
    
class match(object):
    """
    Use for wait a series conditions and return their result to a list.
    
    @code
    checkcode, password = WebDriverWait(driver, 10).until(EC.match(
        EC.C(EC.xpath_find("//input[@id='fm-login-checkcode']")),
        EC.C(EC.xpath_find("//input[@id='fm-login-password']")),
    ))
    matched_elements.checkcode.clear()
    @endcode
    """
    
    def __init__(self, *conditions, matched_at_least=1):
        self.__conditions = conditions
        self.__matched_at_least = matched_at_least

    def __call__(self, driver):
        elements = []
        for i in range(0, len(self.__conditions)):
            v = self.__conditions[i]
            elements.append(None)
            
            value = v["condition"](driver)
            if False != value:
                elements[i] = value
            elif v["required"]:               
                # If required flag is True and value is False, we return False                
                return False
            
        if len(elements) < self.__matched_at_least:
            return False
        
        return elements
  
class xpath_find(object):
    def __init__(self, xpath_expr, conditions=[]):
        self.__xpath_expr = xpath_expr
        self.__conditions = conditions

    def __call__(self, driver):
        try:
            return driver.xpath_find(self.__xpath_expr, 
                conditions=self.__conditions)
        except NoSuchElementException:
            # Because wait method will invoke xpath_find() multi-times, 
            # can't find the element is a normal state, so we must not 
            # scare.
            return False        
        except WebDriverException as e:
            if "element is not attached to the page document" in str(e):
                return False
            
            raise
        
class xpath_find_all(object):
    """
    Easily to wait until find all elements recursively.
    
    Example : 
    
    @code
    elements = WebDriverWait(driver, 10).until(EC.xpath_find(
        "//input[@id='fm-login-id']",
        conditions=[eecf_visible_of(True)]))
    @endcode 
    """
    def __init__(self, xpath_expr, conditions=[]):
        self.__xpath_expr = xpath_expr
        self.__conditions = conditions

    def __call__(self, driver):
        elements = driver.xpath_find_all(self.__xpath_expr, 
            conditions=self.__conditions)
        if len(elements) > 0:
            return elements
        else:
            return False
        
class xpath_not_existed(object):
    def __init__(self, xpath_expr):
        self.__xpath_expr = xpath_expr

    def __call__(self, driver):
        try:
            driver.xpath_find(self.__xpath_expr)
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
        self.__url = url

    def __call__(self, driver):
        return driver.current_url != self.__url
    
class url_changed_to(object):
    """
    Wait until webdriver's current url changed to specific url
    
    @param regex_object: The target url should be match to this regex!
    """
    def __init__(self, regex_object):
        self.__regex_object = regex_object

    def __call__(self, driver):
        return (self.__regex_object.match(self.__regex_object) is not None)
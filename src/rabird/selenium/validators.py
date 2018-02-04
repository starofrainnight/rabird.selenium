# -*- coding: UTF-8 -*-
from selenium.exceptions import StaleElementReferenceException, \
    NoSuchElementException


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


class eecf_visible_any(eecf_visible_of):

    def __init__(self):
        super().__init__(None)

    def __call__(self, element):
        try:
            # Empty statement just check element is valid
            element.is_displayed()
            return True
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

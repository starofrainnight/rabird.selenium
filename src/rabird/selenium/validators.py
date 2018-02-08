# -*- coding: UTF-8 -*-
from .exceptions import StaleElementReferenceException, \
    NoSuchElementException


class StaleOf(object):

    def __init__(self, check_status):
        self.__check_status = check_status

    def __call__(self, element):
        try:
            # Calling any method forces a staleness check
            element.is_enabled()
            return self.__check_status
        except StaleElementReferenceException:
            return not self.__check_status


class Stale(StaleOf):

    def __init__(self):
        super().__init__(True)


class Fresh(StaleOf):

    def __init__(self):
        super().__init__(False)


class VisibleOf(object):

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


class VisibleAny(VisibleOf):

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


class Visible(VisibleOf):

    def __init__(self):
        super().__init__(True)


class Invisible(VisibleOf):

    def __init__(self):
        super().__init__(False)


class Existed(object):
    """
    This validator only use to check if element existed, don't care if
    it visible or not.
    """

    def __init__(self):
        pass

    def __call__(self, element):
        return element is not None


class SelectOf(object):

    def __init__(self, check_status):
        self.__check_status = check_status

    def __call__(self, element):
        return element.is_selected() == self.__check_status


class Selected(SelectOf):

    def __init__(self):
        super().__init__(True)


class Deselected(SelectOf):

    def __init__(self):
        super().__init__(False)


class EnableOf(object):

    def __init__(self, check_status):
        self.__check_status = check_status

    def __call__(self, element):
        """ Wait until an element is enabled
        returns False otherwise.
        """
        # Calling any method forces a staleness check
        return element.is_enabled() == self.__check_status


class Enabled(EnableOf):

    def __init__(self):
        super().__init__(True)


class Disabled(EnableOf):

    def __init__(self):
        super().__init__(False)


class Operator(list):
    pass


class And(Operator):

    def __init__(self, *args):
        super().__init__(args)

    def __call__(self, element):
        for validator in self:
            if not validator(element):
                return False

        return True


class Or(Operator):

    def __init__(self, *args):
        super().__init__(args)

    def __call__(self, element):
        for validator in self:
            if validator(element):
                return True

        return False


class Not(Operator):

    def __init__(self, validator):
        super().__init__([validator])

    def __call__(self, element):
        return not self[0](element)


class EC2V(object):
    """
    Convert expected condition to validator
    """

    def __init__(self, ec):
        self._ec = ec

    def __call__(self, element):
        return self._ec(element.parent)

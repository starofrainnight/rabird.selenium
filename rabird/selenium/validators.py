# -*- coding: utf-8 -*-
import warnings
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchElementException,
)


def _ensure_list_are_validators(validators):
    """Make sure elements in list validators are validators, we will convert
    it to validators if there mixed with expected conditions.
    """

    for i in range(0, len(validators)):
        if isinstance(validators[i], Validator):
            continue

        # Not validator (may be expected conditions), convert them to
        # validators
        validators[i] = EC2V(validators[i])

    return validators


class Validator(object):
    def __init__(self):
        pass

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __not__(self):
        return Not(self)

    def __bool__(self):
        raise NotImplementedError(
            "Unsupported logical operators just like 'and', 'or' or 'not'!"
            " Use '&', '|' or '~' instead!"
        )


class StaleOf(Validator):
    def __init__(self, check_status):
        super().__init__()

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


class VisibleOf(Validator):
    def __init__(self, check_status):
        super().__init__()

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

        warnings.warn("use 'Existed' instead", DeprecationWarning)

    def __call__(self, element):
        try:
            # Empty statement just check element is valid
            element.is_displayed()
            return True
        except (NoSuchElementException, StaleElementReferenceException):
            # These exceptions are means element disapperred.
            # So it's not in any visible status!
            return False


class Visible(VisibleOf):
    def __init__(self):
        super().__init__(True)


class Invisible(VisibleOf):
    def __init__(self):
        super().__init__(False)


class Existed(VisibleAny):
    """
    This validator only use to check if element existed, don't care if
    it visible or not.
    """

    def __init__(self):
        super().__init__()


class SelectOf(Validator):
    def __init__(self, check_status):
        super().__init__()

        self.__check_status = check_status

    def __call__(self, element):
        return element.is_selected() == self.__check_status


class Selected(SelectOf):
    def __init__(self):
        super().__init__(True)


class Deselected(SelectOf):
    def __init__(self):
        super().__init__(False)


class EnableOf(Validator):
    def __init__(self, check_status):
        super().__init__()

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


class Operator(Validator):
    def __init__(self):
        super().__init__()

        self.members = list()

    def __len__(self):
        return len(self.members)

    def __getitem__(self, name):
        return self.members[name]

    def __contains__(self, name):
        return name in self.members

    def __iter__(self):
        return iter(self.members)


class And(Operator):
    def __init__(self, *args):
        super().__init__()

        self.members += _ensure_list_are_validators(args)

    def __call__(self, element):
        for validator in self.members:
            if not validator(element):
                return False

        return True


class Or(Operator):
    def __init__(self, *args):
        super().__init__()

        self.members += _ensure_list_are_validators(args)

    def __call__(self, element):
        for validator in self.members:
            if validator(element):
                return True

        return False


class Not(Operator):
    def __init__(self, validator):
        super().__init__()

        input_validators = [validator]
        self.members += _ensure_list_are_validators(input_validators)

    def __call__(self, element):
        return not self.members[0](element)


class EC2V(Validator):
    """
    Convert expected condition to validator
    """

    def __init__(self, ec):
        super().__init__()

        self._ec = ec

    def __call__(self, element):
        return self._ec(element.parent)

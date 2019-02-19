from selenium.webdriver import Firefox as WebDriverClass
from .common import Relation

# geckodriver support is best in Firefox 55 and greater, so don't support
# Firefox 54 and below. You could
#
# reference : https://github.com/mozilla/geckodriver#supported-firefoxen
relations = [
    Relation("0.19.1", "55", "3.4", ""),
    Relation("0.15.0", "55", "3.3", ""),
]

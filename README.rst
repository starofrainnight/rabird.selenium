===============
rabird.selenium
===============


.. image:: https://img.shields.io/pypi/v/rabird.selenium.svg
    :target: https://pypi.python.org/pypi/rabird.selenium

.. image:: https://travis-ci.org/starofrainnight/rabird.selenium.svg?branch=master
    :target: https://travis-ci.org/starofrainnight/rabird.selenium

.. image:: https://ci.appveyor.com/api/projects/status/github/starofrainnight/rabird.selenium?svg=true
    :target: https://ci.appveyor.com/project/starofrainnight/rabird.selenium

An extension library for selenium.

This library is an extension library build on top of selenium.

It provided a bunch features that need in production enviroment but selenium
have not provide yet or won't provided by design even in future:

- Added force_xxx() series functions to invoke the element directly even the
  element be covered by other elements. Just as force_click(), force_focus(),
  etc...
- Added force_get() method to webdriver, it will stop the page loading after
  page loading timeout exception happen, so that the next script could just
  run without break by that exception.
- Added ability to set element's attribute
- Provided xpath_find(), xpath_find_all(), etc. For simply invoke xpath for
  recursively find elements. it would iterate each frame and each window to
  find your elements and do the actions without switch frame manually, that
  could reduce a great lot jobs.
- Provided some advance UI class to wrap for some third-parties editors ( Just
  like TinyMCE )

* License: Apache-2.0

Usage
-----

Simple xpath_find_all() sample:

::

    import time
    import rabird.selenium
    rabird.selenium.monkey_patch()
    from rabird.selenium import webdriver

    driver = webdriver.Chrome()
    webdriver.set_recommend_preferences(driver)

    driver.force_get("http://www.bing.com")

    elements = driver.xpath_find_all("//*[@id='sb_form_q']")

    print(elements)

    time.sleep(10)

Credits
---------

This package was created with Cookiecutter_ and the `PyPackageTemplate`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`PyPackageTemplate`: https://github.com/starofrainnight/rtpl-pypackage


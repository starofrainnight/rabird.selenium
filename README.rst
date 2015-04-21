rabird.selenium
---------------

This library is an extension library build on top of selenium.

It provided a bunch features that need in production enviroment but selenium 
have not provide yet or won't provide by design even in future:

- Added force_xxx() series functions to invoke the element directly even the 
  element be covered by other elements. Just as force_click(), force_focus(), 
  etc...
- Added force_get() method to webdriver, it will stop the page loading after 
  page loading timeout exception happen, so that the next script could just 
  run without break by that exception.  
- Provide recursive ability to all functions, it would iterate each frame and
  each window to find your elements and do the actions without switch frame 
  manually, that could reduce a great lot jobs. (Default behavior changed!)
  This feature is disabled by default, you could set 
  webdriver.is_find_element_recursively to True to enable it.   
- Added ability to set element's attribute
- Provided a powerful wait_element() method to wait a specific element, sometimes
  we need to wait some element appear or wait them disappear or wait some status
  changed.
- Provided xpath_select(), xpath_select_all(), xpath_wait(), so does css_xxx().
- Provided some advance UI class to wrap for some third-parties editors ( Just 
  like TinyMCE )

"""
@date 2014-12-17
@author Hong-She Liang <starofrainnight@gmail.com>
"""

import sys
import os
import os.path
import time
import traceback
import threading
import queue
import socket
import whichcraft

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import *
from rabird.core.configparser import ConfigParser
from multiprocessing import Queue
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.remote_connection import (
    RemoteConnection as CommonRemoteConnection,
)
from selenium.webdriver.chrome.remote_connection import ChromeRemoteConnection
from selenium.webdriver.firefox.remote_connection import (
    FirefoxRemoteConnection,
)
from selenium.webdriver.firefox.extension_connection import (
    ExtensionConnection as FirefoxExtensionConnection,
)
from .. import expected_conditions as EC
from ..webdriver.dockerized.webdriver import WebDriver as Dockerized


class WatchDog(object):
    (FEED, STOP) = range(0, 2)

    def __init__(self):
        self.__queue = Queue()
        # Default timeout value set to 3 minute, if we does not have any
        # action at 3 minutes, we terminate the monitoring process
        self.__timeout = 3 * 60.0

    @property
    def timeout(self):
        """Get current timeout value."""
        return self.__timeout

    @timeout.setter
    def timeout(self, value):
        """Set current timeout value"""
        self.__timeout = value

    def _internal_daemon(self, process):
        process.join()

        # Force watcher exit queue waitting...
        self.feed()

    def watch(self, process):

        # Daemon thread to force watch loop exit after process exited.
        daemon_thread = threading.Thread(
            target=self._internal_daemon, args=[process]
        )
        # Set thread to daemon thread, so that we could exit this script
        # if any exceptions happended.
        daemon_thread.daemon = True
        daemon_thread.start()

        last_formatted_stack = [None]
        while True:
            # Process exited, we continue loop until it send STOP command
            if not process.is_alive():
                time.sleep(3)  # Wait for a while
                raise TimeoutError("Process exited without send STOP command!")

            try:
                # Feeder enter message needs not timeout value, we just wait until an
                # enter command
                item = self.__queue.get(True, self.__timeout)

                if item[0] == self.STOP:
                    # Successed to stop watchdog ...
                    break

                # Command format :
                # [self.FEED, formatted_stack]
                last_formatted_stack = item[1]

            except queue.Empty:
                try:
                    # Ignored all exceptions during terminate, so that
                    # we could raise our timeout error exception.
                    process.terminate()
                except:
                    pass
                raise TimeoutError("".join(last_formatted_stack[:-1]))

    def feed(self):
        self.__queue.put([self.FEED, traceback.format_stack()])

    def stop(self):
        self.__queue.put([self.STOP])


def force_get(self, url):
    """
    Loads a web page in the current browser session.

    The differents between get() and force_get() is force_get() will stop
    the page loading process after page load timeout happened and
    pretend the page already loaded. And force_get() will also ignored
    all popup windows that stop next page loading.

    @warning: If you want this method to works as expected, you must set the
    correct page load timeout value by set_page_load_timeout() before
    using. Otherwise, it works just like the get() and block there
    infinite.
    """
    try:
        # Ignore all popup windows and force to load the url.
        original_url = self.current_url

        # If original_url equal to url, that will lead EC.url_changed() never
        # return True!
        if original_url == url:
            condition = EC.url_changed_to(url)
        else:
            condition = EC.url_changed(original_url)

        for i in range(0, 3):  # Try three times
            self.execute_script("window.onbeforeunload = function(e){};")
            self.get(url)

            # Next code statements are just use for Chrome browser.
            # It will not ensure the url be success navigated to, so we
            # will try 3 times until failed.
            try:
                WebDriverWait(self, 10).until(condition)
                break
            except TimeoutException:
                pass
    except TimeoutException as e:
        # Stop the page loading if timeout already happened.
        self.execute_script("window.stop()")

    return self


def open_window(self, name="", features=None):
    params = []
    params.append("''")  # Open empty window first
    params.append("'%s'" % name)
    if features:
        params.append("'%s'" % features)

    self.execute_script("window.open(%s)" % ",".join(params))
    time.sleep(1)
    return self.window_handles[-1]


def close_window(self, handle):
    old_handle = self.current_window_handle
    self.switch_to.window(handle)
    self.close()
    if handle != old_handle:
        self.switch_to.window(old_handle)


def set_timeouts_safety(self, timeout):
    """
    A safe way to set timeouts of page loading, xpath waitting and command
    executing.

    It will keep command executor's timeout value longer than other timeout
    values, because webdriver break if command executor timeout!

    So if other timeout value longer than command executor's timeout value,
    they won't take effect because webdriver will break before they works.

    There no way to get safe timeout value, but if you have not specific those
    timeout values, you could get the page loading timeout value as the safe
    timeout value.
    """

    self.set_page_load_timeout(timeout)
    # Command timeout value be setted to 45 seconds
    # FIXME: Seems the whole webdriver broken if command executor timeout!
    self.command_executor.set_timeout(timeout + 15.0)
    self.set_xpath_wait_timeout(timeout)


def get_xpath_wait_timeout(self):
    """
    Get xpath wait timeout value, default to 30 seconds
    """

    if "_xpath_wait_timeout" in self.__dict__:
        return self._xpath_wait_timeout
    else:
        return 30.0


def set_xpath_wait_timeout(self, timeout):
    self._xpath_wait_timeout = timeout


def set_watchdog(self, watchdog):
    self._watchdog = watchdog


def get_watchdog(self):
    if hasattr(self, "_watchdog"):
        return self._watchdog

    return None


def get_pid(self):
    """A unified way to get spawned webdriver process id (Not the browser's!)

    :raises NotImplementedError: If the webdriver unsupported yet.
    :return: WebDriver's process ID
    :rtype: int
    """

    # References to
    # https://stackoverflow.com/questions/10752512/get-pid-of-browser-launched-by-selenium
    if isinstance(self, Firefox):
        return self.binary.process.pid

    if hasattr(self, "service") and hasattr(self.service, "process"):
        return self.service.process.pid

    raise NotImplementedError("Unsupported webdriver!")


def execute(self, driver_command, params=None):
    """
    All commands will pass to this function. So we just need to feed the
    watchdog here to avoid doing execution infinite here ...
    """
    if self.get_watchdog() is not None:
        self.get_watchdog().feed()

    try:
        return self._old_execute(driver_command, params)
    except (socket.timeout, TimeoutException):
        self._restart_connection()
        raise


def if_failed_retry(
    self, executor, validator=lambda: False, retry_times=3, interval=1.0
):
    for i in range(0, retry_times):
        try:
            result = executor()
            validated_result = validator()
            if False != validated_result:
                break
        except Exception as e:
            traceback.print_exc()
            if i >= (retry_times - 1):
                raise  # Reraise the last exception

        time.sleep(interval)
    return result


def get_chrome_default_arguments():
    options = ChromeOptions()

    args = {}
    args["chrome_options"] = options

    # If we can't find default chromedriver, we search chromium-browser's
    # chromedriver
    driver_path = whichcraft.which("chromedriver")
    if driver_path:
        user_data_dir = "~/.config/google-chrome/Default"
    else:
        driver_path = "/usr/lib/chromium-browser/chromedriver"
        if os.path.exists(driver_path):
            user_data_dir = "~/.config/chromium/Default"

    if os.path.exists(driver_path):
        user_data_dir = os.path.normpath(os.path.expanduser(user_data_dir))
        options.add_argument("--user-data-dir=%s" % user_data_dir)

        args["executable_path"] = driver_path

    return args


def get_firefox_default_arguments():
    if sys.platform == "win32":
        firefox_config_path = os.path.normpath(
            os.path.expandvars("$APPDATA/Mozilla/Firefox/profiles.ini")
        )
    else:
        firefox_config_path = os.path.normpath(
            os.path.expanduser("~/.mozilla/firefox/profiles.ini")
        )

    config = ConfigParser()
    config.readfp(open(firefox_config_path))
    profile_path = ""
    for section_name in config.sections():
        if not section_name.startswith("Profile"):
            continue

        if config.has_option(section_name, "Default") and (
            config.getint(section_name, "Default", fallback=0) == 1
        ):
            if config.getint(section_name, "IsRelative", fallback=0) == 1:
                profile_path = os.path.join(
                    os.path.dirname(firefox_config_path),
                    config.get(section_name, "Path"),
                )
            else:
                profile_path = config.get(section_name, "Path")

            break

    profile = FirefoxProfile(profile_path)
    return {"firefox_profile": profile}


def _restart_connection(self):
    if isinstance(self, Chrome) or isinstance(self, Opera):
        # Fixed chrome connection invalid after timeout !
        self.command_executor = ChromeRemoteConnection(
            remote_server_addr=self.service.service_url
        )
    elif isinstance(self, Firefox):
        # self.capabilities
        try:
            capabilities = self.capabilities["desiredCapabilities"]
        except:
            capabilities = None

        # marionette
        if (self.profile is None) or (
            capabilities and capabilities.get("marionette")
        ):
            self.command_executor = FirefoxRemoteConnection(
                remote_server_addr=self.service.service_url
            )
        else:
            # Oh well... sometimes the old way is the best way.
            self.command_executor = FirefoxExtensionConnection(
                "127.0.0.1", self.profile, self.binary, 30
            )

    else:
        self.command_executor = CommonRemoteConnection(
            self.command_executor._url,
            keep_alive=self.command_executor.keep_alive,
        )


def set_recommend_preferences(self):
    # All other timeout values except this one must be set after first
    # command sended.
    self.set_page_load_timeout(30)
    self.set_window_position(0, 0)
    self.set_window_size(800, 600)
    # Don't invoke set_timeouts_safety() before codes above, otherwise the
    # firefox sometimes will freeze when waitting response (just like the 'get'
    # function).
    self.set_timeouts_safety(60)

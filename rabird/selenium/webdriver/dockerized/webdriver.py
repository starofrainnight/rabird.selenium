# -*- coding: utf-8 -*-
"""
Provided a series methods that support create local dockerized webdriver.
"""
import docker
import time
import urllib
from attrdict import AttrDict
from selenium.webdriver import Remote
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from .options import Options as DockerizedOptions


def guess_capabilities(image_name):
    contexts = [
        ("chrome", DesiredCapabilities.CHROME),
        ("fireofx", DesiredCapabilities.FIREFOX),
    ]

    for context in contexts:
        if context[0] in image_name.lower():
            return context[1].copy()

    raise IndexError("Unsupported selenium image : %s" % image_name)


class WebDriver(Remote):
    def __init__(
        self, *args, dockerized_options=DockerizedOptions(), **kwargs
    ):
        """
        Start the selenium image with specific container name and create a
        webdriver connected to the container.

        You could view the browser status by follow command :

        vncviewer -viewonly 127.0.0.1:<Runtime Port of 5900>

        The random mapped port of 5900 could get from console:

        docker ps
        """

        self._dockerized_options = dockerized_options

        container_name = (
            "rsdockerized-%s" % self._dockerized_options.container_name
        )
        image_name = self._dockerized_options.image_name
        max_timeout_count = 30

        # Provide docker apis
        dclient = docker.from_env()
        dapi = docker.APIClient()

        # Check if image exists, pull one if not exists
        try:
            dclient.images.get(image_name)
        except docker.errors.ImageNotFound:
            dclient.images.pull(image_name)

        # Check if container with specific containter name existed, stop and remove
        # existed one.
        #
        # If we don't remove the existed one, we will start another browser instance
        # inside the container and left multi-instances to the containters.
        try:
            container = dclient.containers.get(container_name)
            container.stop()

            # Wait container be removed

            # The container should be removed during 30s
            timeout_count = max_timeout_count
            while True:
                time.sleep(1)
                timeout_count -= 1

                try:
                    dclient.containers.get(container_name)
                except docker.errors.NotFound:
                    # Container already success removed.
                    break

                if timeout_count <= 0:
                    # If we tried timeout_count times without get the container
                    # removed, we should report errors
                    raise TimeoutError(
                        "Container not removed after %ss: %s"
                        % (max_timeout_count, container_name)
                    )

        except docker.errors.NotFound:
            pass

        container = dclient.containers.run(
            name=container_name,
            image=image_name,
            # FIXME: Fixed browser crash, but how make it works under windows?
            volumes={"/dev/shm": {"bind": "/dev/shm", "mode": "rw"}},
            # Don't take fixed ports
            ports={"5900": ("127.0.0.1", None), "4444": ("127.0.0.1", None)},
            # FIXME: Seems this variable not working...
            # environment={
            #     'VNC_NO_PASSWORD': 1,
            # },
            detach=True,
            auto_remove=True,
        )

        port = dapi.port(container.id, "4444")[0]

        time.sleep(1)

        # Wait for connected ...
        timeout_count = max_timeout_count
        while True:
            try:
                super().__init__(
                    command_executor="http://%s:%s/wd/hub"
                    % (port["HostIp"], port["HostPort"]),
                    desired_capabilities=guess_capabilities(image_name),
                )

                self._container = container
                # Break the waitting loop if success connected
                break
            except (urllib.error.URLError, ConnectionResetError):
                time.sleep(1)
                timeout_count -= 1

                if timeout_count <= 0:
                    # If we tried timeout_count times without get the container
                    # removed, we should report errors
                    raise TimeoutError(
                        "Container can't connect to : %s" % container_name
                    )

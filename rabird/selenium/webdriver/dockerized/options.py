# -*- coding: utf-8 -*-


class Options(object):
    def __init__(self):
        self._container_name = "rsdockerized"
        self._image_name = "selenium/standalone-chrome-debug:latest"

    @property
    def container_name(self):
        return self._container_name

    @container_name.setter
    def container_name(self, value):
        self._container_name = value

    @property
    def image_name(self):
        return self._image_name

    @image_name.setter
    def image_name(self, value):
        self._image_name = value

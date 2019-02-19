def frame(self, frame_reference):
    """Added support switch to a frame where guide by the path.

    @param frame_path An array that contained frame ids how we could get to the
    final frame.
    """
    if isinstance(frame_reference, list):
        # First we should switch to frame window, the first element of frame
        # path is the window's handle!
        frame_window = frame_reference[0]
        self._driver.switch_to.window(frame_window)
        self._driver.switch_to.default_content()

        frame_path = frame_reference[1:]
        for reference in frame_path:
            self._old_frame(reference)
    else:
        self._old_frame(frame_reference)

    return self

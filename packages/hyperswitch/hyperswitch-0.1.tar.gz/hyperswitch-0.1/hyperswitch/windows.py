
class ActiveWindowRepository(object):
    _exclusion_list = [None, "Desktop"]

    def __init__(self, wm_interface):
        self._wm_interface = wm_interface

    def load_windows(self):
        clients = self._wm_interface.getClientListStacking()

        windows = []

        for client in clients:
            name = self._wm_interface.getWmName(client)
            if name not in ActiveWindowRepository._exclusion_list:
                windows.append(Window(self._wm_interface, client, name))

        # Reverse the order so that the most recent window is on top
        windows.reverse()
        return windows


class Window(object):
    def __init__(self, wm_interface, wm_id, title):
        self._wm_interface = wm_interface
        self.id = wm_id
        self.title = title

    def bring_to_front(self):
        print "Bring to front: " + self.title
        self._wm_interface.setActiveWindow(self.id)
        self._wm_interface.display.flush()

    def __str__(self):
        return "<Window: " + self.title + ">"

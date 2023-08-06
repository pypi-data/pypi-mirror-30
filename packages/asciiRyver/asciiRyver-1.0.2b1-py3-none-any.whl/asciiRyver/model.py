import threading

class Model(object):
    def __init__(self):
        self.running = object
        self.activeClient = object
        self._signal = threading.Event()
        self._messageQueue = []
        self._chatwidth = int

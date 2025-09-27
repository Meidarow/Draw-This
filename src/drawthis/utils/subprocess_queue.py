import multiprocessing
import queue
from drawthis.app.signals import session_started, session_ended

class SignalQueue:
    def __init__(self):
        self.signal_queue = multiprocessing.Queue()
        self.signals = {
            "session_started": session_started,
            "session_ended": session_ended
        }

    def send(self, signal_name: str, **kwargs):
        self.signal_queue.put((signal_name, kwargs))

    def poll_queue(self):
        try:
            signal_name, kwargs = self.signal_queue.get_nowait()
            self.signals[signal_name].send("SignalQueue",**kwargs)
        except queue.Empty:
            return
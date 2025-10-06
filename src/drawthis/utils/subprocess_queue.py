import multiprocessing
import queue
from drawthis.app.signals import session_started, session_ended

class SignalQueue:
    def __init__(self):
        ctx = multiprocessing.get_context('spawn')
        self.queue = ctx.Queue()
        self.signals = {
            "session_started": session_started,
            "session_ended": session_ended
        }

    def poll_queue(self):
        try:
            signal_name = self.queue.get_nowait()
            kwargs = {}
            self.signals[signal_name].send("SignalQueue",**kwargs)
        except queue.Empty:
            return
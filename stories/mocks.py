# A fake bus that just prints what it gets
class MockCommandBus:
    def register(self, *args):
        pass  # We don't care

    @staticmethod
    def dispatch(command):
        print(f"[MockCommandBus] Dispatched: {command}")


class MockEventBus:
    def subscribe(self, *args):
        pass  # We don't care

    @staticmethod
    def publish(event):
        print(f"[MockEventBus] Published: {event}")

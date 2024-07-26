from log import Log

class Notifier:
    def notify(self, message: str) -> None:
        Log.L(Log.I, message)
        self.send_notification(message)

    def send_notification(self, message: str) -> None:
        return None

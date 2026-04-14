import signal


class TimeoutException(Exception):
    pass


def _handle_timeout(signum, frame):
    raise TimeoutException("Operation timed out")


class time_limit:
    def __init__(self, seconds):
        self.seconds = seconds

    def __enter__(self):
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc, tb):
        signal.alarm(0)
        return False
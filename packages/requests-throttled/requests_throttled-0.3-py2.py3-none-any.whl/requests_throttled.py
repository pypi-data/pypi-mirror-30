import requests
import time


def throttle(Session):
    class ThrottledSession(Session):

        def __init__(self, *args, **kwargs):
            self.rate = kwargs.pop('rate')
            self.last = 0
            super().__init__(*args, **kwargs)

        def _wait(self):
            cur = time.time()
            next = self.last + (1 / self.rate)
            if cur < next:
                time.sleep(next - cur)
            self.last = time.time()

        def send(self, *args, **kwargs):
            self._wait()
            return super().send(*args, **kwargs)

    return ThrottledSession


Session = throttle(requests.Session)

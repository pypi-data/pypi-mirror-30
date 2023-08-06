# requests_throttled

Provides a simple class decorator `throttle` to be used on
`requests.Session` or subclasses. It adds a required keyword argument
`rate` to class's constructor, which is a maximum number of requests
per second that session will be sending. Blocks to wait until it is
allowed to send next request.

It works by creating a subclass with overriden `send` method.

```
from requests_throttled import Session
with Session(rate=2) as s:
  ...  # use `s` here, won't allow more than 2 requests per second
```

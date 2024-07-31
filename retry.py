from collections.abc import Callable, Iterable
from time import sleep
from util import HikApiException

class HikApiTimeoutException(HikApiException):
  pass

def retry(func: Callable[[], None], iterator: Iterable[float]) -> None:
  for t in iterator:
    if t > 0:
      sleep(t)
    try:
      func()
      return
    except HikApiTimeoutException:
      continue
  
  raise HikApiTimeoutException

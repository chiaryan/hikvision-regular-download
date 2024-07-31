from itertools import chain, repeat
from collections.abc import Iterator

def _takewhilesum(it: Iterator[float], limit: float):
  total: float = 0
  while total < limit:
    n = next(it)
    total += n
    yield n

def linear(c: float, step: float, limit: float):
  return _takewhilesum(chain([c], repeat(step)), limit)

def _exph(base, pow):
  n = base
  while True:
    yield n
    n *= pow

def exponential(c: float, base: float, pow: float, limit: float):
  return _takewhilesum(chain([c], _exph(base, pow)), limit)

"""Working Memory - minimal version (spec §4.4): a fixed-capacity buffer
of the most recent items. capacity=0 means nothing is ever retained."""

from collections import deque
from collections.abc import Iterator


class WorkingMemory[T]:
    def __init__(self, capacity: int) -> None:
        if capacity < 0:
            raise ValueError("capacity must be >= 0")
        self.capacity = capacity
        self._buffer: deque[T] = deque(maxlen=capacity)

    def add(self, item: T) -> None:
        self._buffer.append(item)

    def __len__(self) -> int:
        return len(self._buffer)

    def __iter__(self) -> Iterator[T]:
        return iter(self._buffer)

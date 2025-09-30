import time
from typing import TypeVar, Callable, Generic, Iterable, Type
from agno.utils.log import log_warning

W = TypeVar("W")
T = TypeVar("T")

class WrapperHandler(Generic[W]):
    def __init__(self, wrappers: list[W], try_per_wrapper: int = 3, retry_delay: int = 2):
        self.wrappers = wrappers
        self.retry_per_wrapper = try_per_wrapper
        self.retry_delay = retry_delay
        self.index = 0
        self.retry_count = 0

    def try_call(self, func: Callable[[W], T]) -> T:
        iterations = 0
        while iterations < len(self.wrappers):
            print(f"Trying wrapper {self.index}")
            try:
                wrapper = self.wrappers[self.index]
                result = func(wrapper)
                self.retry_count = 0
                return result
            except Exception as e:
                self.retry_count += 1
                print(f"Error occurred {self.retry_count}/{self.retry_per_wrapper}: {e}")
                if self.retry_count >= self.retry_per_wrapper:
                    self.index = (self.index + 1) % len(self.wrappers)
                    self.retry_count = 0
                    iterations += 1
                else:
                    log_warning(f"{wrapper} failed {self.retry_count}/{self.retry_per_wrapper}: {e}")
                    time.sleep(self.retry_delay)

        raise Exception(f"All wrappers failed after retries")

    @staticmethod
    def build_wrappers(constructors: Iterable[Type[W]], try_per_wrapper: int = 3, retry_delay: int = 2) -> 'WrapperHandler[W]':
        result = []
        for wrapper_class in constructors:
            try:
                wrapper = wrapper_class()
                result.append(wrapper)
            except Exception as e:
                log_warning(f"{wrapper_class} cannot be initialized: {e}")

        return WrapperHandler(result, try_per_wrapper, retry_delay)
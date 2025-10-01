import time
import traceback
from typing import TypeVar, Callable, Generic, Iterable, Type
from agno.utils.log import log_warning, log_info

W = TypeVar("W")
T = TypeVar("T")

class WrapperHandler(Generic[W]):
    """
    A handler for managing multiple wrappers with retry logic.
    It attempts to call a function on the current wrapper, and if it fails,
    it retries a specified number of times before switching to the next wrapper.
    If all wrappers fail, it raises an exception.

    Note: use `build_wrappers` to create an instance of this class for better error handling.
    """

    def __init__(self, wrappers: list[W], try_per_wrapper: int = 3, retry_delay: int = 2):
        """
        Initializes the WrapperHandler with a list of wrappers and retry settings.\n
        Use `build_wrappers` to create an instance of this class for better error handling.
        Args:
            wrappers (list[W]): A list of wrapper instances to manage.
            try_per_wrapper (int): Number of retries per wrapper before switching to the next.
            retry_delay (int): Delay in seconds between retries.
        """
        assert not WrapperHandler.__check(wrappers), "All wrappers must be instances of their respective classes. Use `build_wrappers` to create the WrapperHandler."

        self.wrappers = wrappers
        self.retry_per_wrapper = try_per_wrapper
        self.retry_delay = retry_delay
        self.index = 0
        self.retry_count = 0

    def try_call(self, func: Callable[[W], T]) -> T:
        """
        Attempts to call the provided function on the current wrapper.
        If it fails, it retries a specified number of times before switching to the next wrapper.
        If all wrappers fail, it raises an exception.
        Args:
            func (Callable[[W], T]): A function that takes a wrapper and returns a result.
        Returns:
            T: The result of the function call.
        Raises:
            Exception: If all wrappers fail after retries.
        """
        iterations = 0
        while iterations < len(self.wrappers):
            try:
                wrapper = self.wrappers[self.index]
                log_info(f"Trying wrapper: {wrapper} - function {func}")
                result = func(wrapper)
                self.retry_count = 0
                return result
            except Exception as e:
                self.retry_count += 1
                log_warning(f"{wrapper} failed {self.retry_count}/{self.retry_per_wrapper}: {WrapperHandler.__concise_error(e)}")

                if self.retry_count >= self.retry_per_wrapper:
                    self.index = (self.index + 1) % len(self.wrappers)
                    self.retry_count = 0
                    iterations += 1
                else:
                    time.sleep(self.retry_delay)

        raise Exception(f"All wrappers failed after retries")

    def try_call_all(self, func: Callable[[W], T]) -> dict[str, T]:
        """
        Calls the provided function on all wrappers, collecting results.
        If a wrapper fails, it logs a warning and continues with the next.
        If all wrappers fail, it raises an exception.
        Args:
            func (Callable[[W], T]): A function that takes a wrapper and returns a result.
        Returns:
            list[T]: A list of results from the function calls.
        Raises:
            Exception: If all wrappers fail.
        """
        results = {}
        log_info(f"All wrappers: {[wrapper.__class__ for wrapper in self.wrappers]} - function {func}")
        for wrapper in self.wrappers:
            try:
                result = func(wrapper)
                results[wrapper.__class__] = result
            except Exception as e:
                log_warning(f"{wrapper} failed: {WrapperHandler.__concise_error(e)}")
        if not results:
            raise Exception("All wrappers failed")
        return results

    @staticmethod
    def __check(wrappers: list[W]) -> bool:
        return all(w.__class__ is type for w in wrappers)

    @staticmethod
    def __concise_error(e: Exception) -> str:
        last_frame = traceback.extract_tb(e.__traceback__)[-1]
        return f"{e} [\"{last_frame.filename}\", line {last_frame.lineno}]"

    @staticmethod
    def build_wrappers(constructors: Iterable[Type[W]], try_per_wrapper: int = 3, retry_delay: int = 2, kwargs: dict | None = None) -> 'WrapperHandler[W]':
        """
        Builds a WrapperHandler instance with the given wrapper constructors.
        It attempts to initialize each wrapper and logs a warning if any cannot be initialized.
        Only successfully initialized wrappers are included in the handler.
        Args:
            constructors (Iterable[Type[W]]): An iterable of wrapper classes to instantiate. e.g. [WrapperA, WrapperB]
            try_per_wrapper (int): Number of retries per wrapper before switching to the next.
            retry_delay (int): Delay in seconds between retries.
            kwargs (dict | None): Optional dictionary with keyword arguments common to all wrappers.
        Returns:
            WrapperHandler[W]: An instance of WrapperHandler with the initialized wrappers.
        Raises:
            Exception: If no wrappers could be initialized.
        """
        assert WrapperHandler.__check(constructors), f"All constructors must be classes. Received: {constructors}"

        result = []
        for wrapper_class in constructors:
            try:
                wrapper = wrapper_class(**(kwargs or {}))
                result.append(wrapper)
            except Exception as e:
                log_warning(f"{wrapper_class} cannot be initialized: {e}")

        return WrapperHandler(result, try_per_wrapper, retry_delay)
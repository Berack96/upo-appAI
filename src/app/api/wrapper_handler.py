import inspect
import time
import traceback
from typing import Any, Callable, Generic, TypeVar
from agno.utils.log import log_info, log_warning #type: ignore

WrapperType = TypeVar("WrapperType")
WrapperClassType = TypeVar("WrapperClassType")
OutputType = TypeVar("OutputType")


class WrapperHandler(Generic[WrapperType]):
    """
    A handler for managing multiple wrappers with retry logic.
    It attempts to call a function on the current wrapper, and if it fails,
    it retries a specified number of times before switching to the next wrapper.
    If all wrappers fail, it raises an exception.

    Note: use `build_wrappers` to create an instance of this class for better error handling.
    """

    def __init__(self, wrappers: list[WrapperType], try_per_wrapper: int = 3, retry_delay: int = 2):
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

    def set_retries(self, try_per_wrapper: int, retry_delay: int) -> None:
        """
        Sets the retry parameters for the handler.
        Args:
            try_per_wrapper (int): Number of retries per wrapper before switching to the next.
            retry_delay (int): Delay in seconds between retries.
        """
        self.retry_per_wrapper = try_per_wrapper
        self.retry_delay = retry_delay

    def try_call(self, func: Callable[[WrapperType], OutputType]) -> OutputType:
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
        return self.__try_call(func, try_all=False).popitem()[1]

    def try_call_all(self, func: Callable[[WrapperType], OutputType]) -> dict[str, OutputType]:
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
        return self.__try_call(func, try_all=True)

    def __try_call(self, func: Callable[[WrapperType], OutputType], try_all: bool) -> dict[str, OutputType]:
        """
        Internal method to handle the logic of trying to call a function on wrappers.
        It can either stop at the first success or try all wrappers.
        Args:
            func (Callable[[W], T]): A function that takes a wrapper and returns a result.
            try_all (bool): If True, tries all wrappers and collects results; if False, stops at the first success.
        Returns:
            dict[str, T]: A dictionary mapping wrapper class names to results.
        Raises:
            Exception: If all wrappers fail after retries.
        """

        log_info(f"{inspect.getsource(func).strip()} {inspect.getclosurevars(func).nonlocals}")
        results: dict[str, OutputType] = {}
        starting_index = self.index

        for i in range(starting_index, len(self.wrappers) + starting_index):
            self.index = i % len(self.wrappers)
            wrapper = self.wrappers[self.index]
            wrapper_name = wrapper.__class__.__name__

            if not try_all:
                log_info(f"try_call {wrapper_name}")

            for try_count in range(1, self.retry_per_wrapper + 1):
                try:
                    result = func(wrapper)
                    log_info(f"{wrapper_name} succeeded")
                    results[wrapper_name] = result
                    break

                except Exception as e:
                    error = WrapperHandler.__concise_error(e)
                    log_warning(f"{wrapper_name} failed {try_count}/{self.retry_per_wrapper}: {error}")
                    time.sleep(self.retry_delay)

            if not try_all and results:
                return results

        if not results:
            error = locals().get("error", "Unknown error")
            raise Exception(f"All wrappers failed, latest error: {error}")

        self.index = starting_index
        return results

    @staticmethod
    def __check(wrappers: list[Any]) -> bool:
        return all(w.__class__ is type for w in wrappers)

    @staticmethod
    def __concise_error(e: Exception) -> str:
        last_frame = traceback.extract_tb(e.__traceback__)[-1]
        return f"{e} [\"{last_frame.filename}\", line {last_frame.lineno}]"

    @staticmethod
    def build_wrappers(constructors: list[type[WrapperClassType]], try_per_wrapper: int = 3, retry_delay: int = 2, kwargs: dict[str, Any] | None = None) -> 'WrapperHandler[WrapperClassType]':
        """
        Builds a WrapperHandler instance with the given wrapper constructors.
        It attempts to initialize each wrapper and logs a warning if any cannot be initialized.
        Only successfully initialized wrappers are included in the handler.
        Args:
            constructors (list[type[W]]): An iterable of wrapper classes to instantiate. e.g. [WrapperA, WrapperB]
            try_per_wrapper (int): Number of retries per wrapper before switching to the next.
            retry_delay (int): Delay in seconds between retries.
            kwargs (dict | None): Optional dictionary with keyword arguments common to all wrappers.
        Returns:
            WrapperHandler[W]: An instance of WrapperHandler with the initialized wrappers.
        Raises:
            Exception: If no wrappers could be initialized.
        """
        assert WrapperHandler.__check(constructors), f"All constructors must be classes. Received: {constructors}"

        result: list[WrapperClassType] = []
        for wrapper_class in constructors:
            try:
                wrapper = wrapper_class(**(kwargs or {}))
                result.append(wrapper)
            except Exception as e:
                log_warning(f"{wrapper_class} cannot be initialized: {e}")

        return WrapperHandler(result, try_per_wrapper, retry_delay)
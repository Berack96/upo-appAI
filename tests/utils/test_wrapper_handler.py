import pytest
from app.utils.wrapper_handler import WrapperHandler

class MockWrapper:
    def do_something(self) -> str:
        return "Success"

class MockWrapper2(MockWrapper):
    def do_something(self) -> str:
        return "Success 2"

class FailingWrapper(MockWrapper):
    def do_something(self):
        raise Exception("Intentional Failure")


class MockWrapperWithParameters:
    def do_something(self, param1: str, param2: int) -> str:
        return f"Success {param1} and {param2}"

class FailingWrapperWithParameters(MockWrapperWithParameters):
    def do_something(self, param1: str, param2: int):
        raise Exception("Intentional Failure")


@pytest.mark.wrapper
class TestWrapperHandler:
    def test_init_failing(self):
        with pytest.raises(AssertionError) as exc_info:
            WrapperHandler([MockWrapper, MockWrapper2])
        assert exc_info.type == AssertionError

    def test_init_failing_empty(self):
        with pytest.raises(AssertionError) as exc_info:
            WrapperHandler.build_wrappers([])
        assert exc_info.type == AssertionError

    def test_init_failing_with_instances(self):
        with pytest.raises(AssertionError) as exc_info:
            WrapperHandler.build_wrappers([MockWrapper(), MockWrapper2()])
        assert exc_info.type == AssertionError

    def test_init_not_failing(self):
        handler = WrapperHandler.build_wrappers([MockWrapper, MockWrapper2])
        assert handler is not None
        assert len(handler.wrappers) == 2
        handler = WrapperHandler([MockWrapper(), MockWrapper2()])
        assert handler is not None
        assert len(handler.wrappers) == 2

    def test_all_wrappers_fail(self):
        wrappers = [FailingWrapper, FailingWrapper]
        handler: WrapperHandler[MockWrapper] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=2, retry_delay=0)

        with pytest.raises(Exception) as exc_info:
            handler.try_call(lambda w: w.do_something())
        assert "All wrappers failed" in str(exc_info.value)

    def test_success_on_first_try(self):
        wrappers = [MockWrapper, FailingWrapper]
        handler: WrapperHandler[MockWrapper] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=2, retry_delay=0)

        result = handler.try_call(lambda w: w.do_something())
        assert result == "Success"
        assert handler.index == 0  # Should still be on the first wrapper
        assert handler.retry_count == 0

    def test_eventual_success(self):
        wrappers = [FailingWrapper, MockWrapper]
        handler: WrapperHandler[MockWrapper] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=2, retry_delay=0)

        result = handler.try_call(lambda w: w.do_something())
        assert result == "Success"
        assert handler.index == 1  # Should have switched to the second wrapper
        assert handler.retry_count == 0

    def test_partial_failures(self):
        wrappers = [FailingWrapper, MockWrapper, FailingWrapper]
        handler: WrapperHandler[MockWrapper] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=1, retry_delay=0)

        result = handler.try_call(lambda w: w.do_something())
        assert result == "Success"
        assert handler.index == 1  # Should have switched to the second wrapper
        assert handler.retry_count == 0

        # Next call should still succeed on the second wrapper
        result = handler.try_call(lambda w: w.do_something())
        assert result == "Success"
        assert handler.index == 1  # Should still be on the second wrapper
        assert handler.retry_count == 0

        handler.index = 2  # Manually switch to the third wrapper
        result = handler.try_call(lambda w: w.do_something())
        assert result == "Success"
        assert handler.index == 1  # Should return to the second wrapper after failure
        assert handler.retry_count == 0

    def test_try_call_all_success(self):
        wrappers = [MockWrapper, MockWrapper2]
        handler: WrapperHandler[MockWrapper] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=1, retry_delay=0)
        results = handler.try_call_all(lambda w: w.do_something())
        assert results == {MockWrapper: "Success", MockWrapper2: "Success 2"}

    def test_try_call_all_partial_failures(self):
        # Only the second wrapper should succeed
        wrappers = [FailingWrapper, MockWrapper, FailingWrapper]
        handler: WrapperHandler[MockWrapper] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=1, retry_delay=0)
        results = handler.try_call_all(lambda w: w.do_something())
        assert results == {MockWrapper: "Success"}

        # Only the second and fourth wrappers should succeed
        wrappers = [FailingWrapper, MockWrapper, FailingWrapper, MockWrapper2]
        handler: WrapperHandler[MockWrapper] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=1, retry_delay=0)
        results = handler.try_call_all(lambda w: w.do_something())
        assert results == {MockWrapper: "Success", MockWrapper2: "Success 2"}

    def test_try_call_all_all_fail(self):
        # Test when all wrappers fail
        handler_all_fail: WrapperHandler[MockWrapper] = WrapperHandler.build_wrappers([FailingWrapper, FailingWrapper], try_per_wrapper=1, retry_delay=0)
        with pytest.raises(Exception) as exc_info:
            handler_all_fail.try_call_all(lambda w: w.do_something())
        assert "All wrappers failed" in str(exc_info.value)

    def test_wrappers_with_parameters(self):
        wrappers = [FailingWrapperWithParameters, MockWrapperWithParameters]
        handler: WrapperHandler[MockWrapperWithParameters] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=2, retry_delay=0)

        result = handler.try_call(lambda w: w.do_something("test", 42))
        assert result == "Success test and 42"
        assert handler.index == 1  # Should have switched to the second wrapper
        assert handler.retry_count == 0

    def test_wrappers_with_parameters_all_fail(self):
        wrappers = [FailingWrapperWithParameters, FailingWrapperWithParameters]
        handler: WrapperHandler[MockWrapperWithParameters] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=1, retry_delay=0)

        with pytest.raises(Exception) as exc_info:
            handler.try_call(lambda w: w.do_something("test", 42))
        assert "All wrappers failed" in str(exc_info.value)

    def test_try_call_all_with_parameters(self):
        wrappers = [FailingWrapperWithParameters, MockWrapperWithParameters]
        handler: WrapperHandler[MockWrapperWithParameters] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=1, retry_delay=0)
        results = handler.try_call_all(lambda w: w.do_something("param", 99))
        assert results == {MockWrapperWithParameters: "Success param and 99"}

    def test_try_call_all_with_parameters_all_fail(self):
        wrappers = [FailingWrapperWithParameters, FailingWrapperWithParameters]
        handler: WrapperHandler[MockWrapperWithParameters] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=1, retry_delay=0)
        with pytest.raises(Exception) as exc_info:
            handler.try_call_all(lambda w: w.do_something("param", 99))
        assert "All wrappers failed" in str(exc_info.value)

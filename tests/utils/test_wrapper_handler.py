import pytest
from app.utils.wrapper_handler import WrapperHandler

class MockWrapper:
    def do_something(self) -> str:
        return "Success"

class FailingWrapper(MockWrapper):
    def do_something(self):
        raise Exception("Intentional Failure")


@pytest.mark.wrapper
class TestWrapperHandler:
    def test_all_wrappers_fail(self):
        wrappers = [FailingWrapper, FailingWrapper]
        handler: WrapperHandler[MockWrapper] = WrapperHandler.build_wrappers(wrappers, try_per_wrapper=2, retry_delay=0)

        with pytest.raises(Exception) as exc_info:
            handler.try_call(lambda w: w.do_something())
        assert "All wrappers failed after retries" in str(exc_info.value)

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

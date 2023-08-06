from unittest.mock import Mock

import pytest

from flask_graphite.hooks import MetricHook, logger


@pytest.fixture
def dumb_hook():
    mock = Mock()
    mock.return_value = ("foo", 42)
    mock.__name__ = "dumb"
    return MetricHook(mock)


def test_dumb_hook_callable(dumb_hook):
    assert callable(dumb_hook)


def test_dumb_hook_name(dumb_hook):
    assert dumb_hook.name == "dumb"


def test_dumb_hook_decorator():
    @MetricHook
    def foo():
        pass

    assert isinstance(foo, MetricHook)


def test_dumb_hook_setup(graphitesend_client, mocked_app, dumb_hook):
    dumb_hook.setup(dumb_hook)
    dumb_hook.register_into(mocked_app)
    assert mocked_app.before_request.called


def test_dumb_hook_setup_decorator(mocked_app, dumb_hook):
    @dumb_hook.setup
    def foo():
        pass

    assert isinstance(foo, MetricHook)


def test_exception_bad_type(mocker, mocked_app, dumb_hook,
                            graphitesend_client):
    mocker.patch.object(logger, "error")
    dumb_hook.type = "invalid_type"
    with pytest.raises(AttributeError):
        dumb_hook.register_into(mocked_app)
    assert logger.error.called


def test_setup_hook_exception_bad_type(mocker, mocked_app, dumb_hook,
                                       graphitesend_client):
    @dumb_hook.setup
    def setup_hook():
        pass

    mocker.patch.object(logger, "error")
    setup_hook.type = "invalid_type"
    with pytest.raises(AttributeError):
        setup_hook.register_into(mocked_app)
    assert logger.error.called


def test_repr(dumb_hook):
    s = repr(dumb_hook)
    assert s == "MetricHook(dumb)"

import pytest
from deepwiki.extraction.strategies import (
    ExtractionStrategy,
    NextJSPushStrategy,
    NextJSDataStrategy,
    RSCStreamStrategy,
    FallbackHTMLStrategy,
    StrategyManager,
)


@pytest.mark.network
def test_nextjs_push_can_handle_returns_bool(fetched_html):
    result = NextJSPushStrategy().can_handle(fetched_html)
    assert isinstance(result, bool)


@pytest.mark.network
def test_nextjs_data_can_handle_returns_bool(fetched_html):
    result = NextJSDataStrategy().can_handle(fetched_html)
    assert isinstance(result, bool)


@pytest.mark.network
def test_rsc_stream_can_handle_returns_bool(fetched_html):
    result = RSCStreamStrategy().can_handle(fetched_html)
    assert isinstance(result, bool)


@pytest.mark.network
def test_fallback_html_can_handle_always_true(fetched_html):
    assert FallbackHTMLStrategy().can_handle(fetched_html) is True


def test_fallback_html_can_handle_empty_string():
    assert FallbackHTMLStrategy().can_handle("") is True


@pytest.mark.network
def test_at_least_one_strategy_extracts_nonempty_content(fetched_html):
    strategies = [
        NextJSPushStrategy(),
        NextJSDataStrategy(),
        RSCStreamStrategy(),
        FallbackHTMLStrategy(),
    ]
    results = [s.extract_content(fetched_html) for s in strategies if s.can_handle(fetched_html)]
    assert any(r.strip() for r in results), "No strategy produced non-empty content"


@pytest.mark.network
def test_strategy_manager_extracts_content_from_fetched_html(fetched_html):
    manager = StrategyManager()
    result = manager.extract_content(fetched_html)
    assert isinstance(result, str)
    assert result.strip()
    assert result != "# No suitable extraction strategy found"


class _DummyStrategy(ExtractionStrategy):
    def can_handle(self, html, url=None):
        return True

    def extract_content(self, html, url=None):
        return "dummy-content"

    def get_priority(self):
        return 5

    def get_name(self):
        return "DummyStrategy"


def test_strategy_manager_add_strategy():
    manager = StrategyManager()
    initial_count = len(manager.strategies)
    manager.add_strategy(_DummyStrategy())
    assert len(manager.strategies) == initial_count + 1
    names = [s.get_name() for s in manager.strategies]
    assert "DummyStrategy" in names


def test_strategy_manager_disable_strategy():
    manager = StrategyManager()
    manager.disable_strategy("NextJSPushStrategy")
    assert "NextJSPushStrategy" in manager.disabled_strategies


def test_strategy_manager_enable_strategy():
    manager = StrategyManager()
    manager.disable_strategy("NextJSPushStrategy")
    manager.enable_strategy("NextJSPushStrategy")
    assert "NextJSPushStrategy" not in manager.disabled_strategies


def test_strategy_manager_disabled_strategy_is_skipped():
    manager = StrategyManager()
    for s in list(manager.strategies):
        manager.disable_strategy(s.get_name())
    manager.add_strategy(_DummyStrategy())
    manager.enable_strategy("DummyStrategy")
    result = manager.extract_content("<html/>")
    assert result == "dummy-content"


def test_strategy_priority_ordering():
    manager = StrategyManager()
    priorities = [s.get_priority() for s in manager.strategies]
    assert priorities == sorted(priorities, reverse=True)


def test_nextjs_push_priority_highest_among_defaults():
    strategies = [
        NextJSPushStrategy(),
        NextJSDataStrategy(),
        RSCStreamStrategy(),
        FallbackHTMLStrategy(),
    ]
    push = next(s for s in strategies if isinstance(s, NextJSPushStrategy))
    fallback = next(s for s in strategies if isinstance(s, FallbackHTMLStrategy))
    assert push.get_priority() > fallback.get_priority()

import pytest
from api import dependencies
from api.services.graph_repository import DemoGraphRepository, PostgresGraphRepository


@pytest.fixture(autouse=True)
def clear_graph_repository_cache() -> None:
    dependencies.get_graph_repository.cache_clear()
    yield
    dependencies.get_graph_repository.cache_clear()


def test_graph_repository_defaults_to_demo(monkeypatch) -> None:
    monkeypatch.delenv("GRAPH_REPOSITORY_MODE", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    repository = dependencies.get_graph_repository()

    assert isinstance(repository, DemoGraphRepository)


def test_graph_repository_uses_postgres_when_explicitly_enabled(monkeypatch) -> None:
    monkeypatch.setenv("GRAPH_REPOSITORY_MODE", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/optewhy")
    repository = dependencies.get_graph_repository()

    assert isinstance(repository, PostgresGraphRepository)

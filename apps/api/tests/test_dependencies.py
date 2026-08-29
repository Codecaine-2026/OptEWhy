import pytest
from api import dependencies
from api.services.graph_repository import PostgresGraphRepository


@pytest.fixture(autouse=True)
def clear_graph_repository_cache() -> None:
    dependencies.get_graph_repository.cache_clear()
    yield
    dependencies.get_graph_repository.cache_clear()


def test_graph_repository_defaults_to_postgres(monkeypatch) -> None:
    monkeypatch.delenv("GRAPH_REPOSITORY_MODE", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/optewhy")
    repository = dependencies.get_graph_repository()

    assert isinstance(repository, PostgresGraphRepository)


def test_graph_repository_rejects_demo_mode(monkeypatch) -> None:
    monkeypatch.setenv("GRAPH_REPOSITORY_MODE", "demo")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/optewhy")

    with pytest.raises(ValueError, match="demo graph data is disabled"):
        dependencies.get_graph_repository()


def test_graph_repository_uses_postgres_when_explicitly_enabled(monkeypatch) -> None:
    monkeypatch.setenv("GRAPH_REPOSITORY_MODE", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/optewhy")
    repository = dependencies.get_graph_repository()

    assert isinstance(repository, PostgresGraphRepository)

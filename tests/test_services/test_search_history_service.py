import pytest

from clible.db.repositories.search_history_repo import SearchHistoryRepo
from clible.services.search_history_service import SearchHistoryService
from clible.services.search_query import SearchQuery


@pytest.fixture
def history_service(db_conn):
    return SearchHistoryService(SearchHistoryRepo(db_conn))


def test_record_and_list_recent(history_service):
    q = SearchQuery(["grace"], mode="phrase", scope="bible")
    history_service.record(q, result_count=42)

    rows = history_service.list_recent()
    assert len(rows) == 1
    assert rows[0]["query_text"] == "grace"
    assert rows[0]["result_count"] == 42


def test_list_recent_limit(history_service):
    for i in range(15):
        q = SearchQuery([f"word{i}"], mode="phrase")
        history_service.record(q, result_count=i)

    rows = history_service.list_recent(limit=10)
    assert len(rows) == 10


def test_clear(history_service):
    q = SearchQuery(["grace"], mode="phrase")
    history_service.record(q, result_count=5)
    deleted = history_service.clear()
    assert deleted == 1
    assert history_service.list_recent() == []

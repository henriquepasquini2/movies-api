import pytest
from unittest.mock import AsyncMock
from services.movies import MoviesService

@pytest.mark.asyncio
async def test_filter_movies_by_id():
    mock_es = AsyncMock()
    mock_es.search_async_scan = AsyncMock(return_value=type('obj', (object,), {'hits': [{'_source': {'id': 1, 'title': 'Test', 'title_normalized': 'test'}}]}))
    service = MoviesService()
    service.es = mock_es
    result = await service.filter_movies('1')
    assert result[0]['id'] == 1

@pytest.mark.asyncio
async def test_filter_movies_by_title_normalized():
    mock_es = AsyncMock()
    mock_es.search_async_scan = AsyncMock(return_value=type('obj', (object,), {'hits': [{'_source': {'id': 2, 'title': 'Test', 'title_normalized': 'test'}}]}))
    service = MoviesService()
    service.es = mock_es
    result = await service.filter_movies('test')
    assert result[0]['title_normalized'] == 'test'

@pytest.mark.asyncio
async def test_filter_movies_by_title_match_fallback():
    mock_es = AsyncMock()
    # First call returns no results, fallback returns one
    mock_es.search_async_scan = AsyncMock(side_effect=[type('obj', (object,), {'hits': []}), type('obj', (object,), {'hits': [{'_source': {'id': 3, 'title': 'Another', 'title_normalized': 'another'}}]})])
    service = MoviesService()
    service.es = mock_es
    result = await service.filter_movies('Another')
    assert result[0]['title'] == 'Another' 
import pytest
from utils.elastic_query import build_term_or_terms_query

def test_build_term_query():
    result = build_term_or_terms_query('title', ['Inception'])
    assert result == {'term': {'title': 'Inception'}}

def test_build_terms_query():
    result = build_term_or_terms_query('genre', ['Drama', 'Crime'])
    assert result == {'terms': {'genre': ['Drama', 'Crime']}} 
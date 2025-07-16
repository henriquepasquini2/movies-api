import pytest
from utils import string_utils

def test_normalized_text_basic():
    assert string_utils.normalized_text('Café') == 'Cafe'
    assert string_utils.normalized_text('ação') == 'acao'
    assert string_utils.normalized_text('João da Silva!') == 'Joao da Silva'

def test_normalized_text_whitespace():
    assert string_utils.normalized_text('  João   da   Silva  ') == 'Joao da Silva'

def test_normalize_alphanumeric():
    assert string_utils.normalize_alphanumeric('abc123!@#') == 'abc123'
    assert string_utils.normalize_alphanumeric('João!@#', keep_whitespaces=True) == 'Joao'
    assert string_utils.normalize_alphanumeric('João!@#', keep_whitespaces=False) == 'Joao'
    assert string_utils.normalize_alphanumeric('João!@#', remove_alphanumeric=False) == 'Joao!@#' 
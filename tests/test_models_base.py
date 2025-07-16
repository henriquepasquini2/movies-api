import pytest
from models.base import BaseAPIModel
from pydantic import ValidationError

class DummyModel(BaseAPIModel):
    name: str

def test_base_api_model_strips_whitespace():
    m = DummyModel(name='  John  ')
    assert m.name == 'John'

def test_base_api_model_forbids_extra():
    with pytest.raises(ValidationError):
        DummyModel(name='John', extra_field='not allowed') 
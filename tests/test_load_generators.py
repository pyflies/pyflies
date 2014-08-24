import pytest

def test_load_generators():

    from pyflies.generators import generator_names


    names = generator_names()

    assert names

import random

import pytest


@pytest.fixture
def input_value():
    input = random.randint(1, 100)
    print(f'FIXTURE ===================  {input} =============================')

    return input


def test_divisible_by_3(input_value):
    print(f'============================ {input} =============================')

    assert input_value % 3 == 0


def test_divisible_by_6(input_value):
    print(f'============================ {input} =============================')

    assert input_value % 6 == 0

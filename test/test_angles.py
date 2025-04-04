import pytest
import numpy as np
from app.pushups import calculate_angle

from app.squats import findAngle


def test_calculate_angle():
    """Test angle calculation between three points."""
    a = [1, 1]
    b = [2, 2]
    c = [3, 3]

    angle = calculate_angle(a, b, c)

    assert isinstance(angle, float)  # Should return a float
    assert 0 <= angle <= 180  # Valid angle range

def test_find_angle():
    a = [1, 1]
    b = [2, 2]
    c = [3, 3]

    angle = findAngle(a, b, c)

    assert isinstance(angle, float)  # Should return a float
    assert 0 <= angle <= 180  # Valid angle range
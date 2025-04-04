import pytest
from app.utils.workout_utils import classify_fitness_level


def test_fitness_classification():
    pushups = 30
    squats = 40
    gender = "Female"
    age = 25

    fitness_level = classify_fitness_level(gender, age, pushups, squats)  # Assume this function exists

    assert isinstance(fitness_level, str), "Fitness level should be a string"
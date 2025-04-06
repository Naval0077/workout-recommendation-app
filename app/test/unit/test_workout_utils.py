import numpy as np
import pytest
from app.models import User, Exercise, Rating
from app import create_app
from app.utils.workout_utils import (
    linear_interpolate,
    get_mean_pushups,
    get_mean_squats,
    get_std_pushups,
    get_std_squats,
    gaussian_pdf,
    get_fitness_level_probabilities,
    classify_fitness_level,
    build_workout_schedule,
    get_training_params_for_goal,
    days_per_week,
    get_next_fitness_level,
    get_difficulty_range_for_next_level
)

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Using in-memory DB for tests
    with app.app_context():
        yield app

@pytest.fixture
def db(app):
    from app import db  # <- not a local SQLAlchemy()
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


# 1. Test: Linear Interpolation
def test_linear_interpolate():
    xp = [20, 30, 40]
    fp = [10, 20, 30]

    result = linear_interpolate(25, xp, fp)
    expected = 15  # Interpolation between (20, 10) and (30, 20)

    assert abs(result - expected) < 0.01


# 2. Test: Get Mean Pushups for Male (Age: 30, Level: 'average')
def test_get_mean_pushups():
    result = get_mean_pushups("male", 30, 'average')
    expected = 19  # Based on the anchors provided in the original code

    assert abs(result - expected) < 0.01


# 3. Test: Get Std Pushups for Male (Age: 30)
def test_get_std_pushups():
    result = get_std_pushups("male", 20, 'average')
    expected = 3.0  # Expected standard deviation value

    assert abs(result - expected) < 0.01


# 4. Test: Gaussian PDF
def test_gaussian_pdf():
    x = 25
    mean = 20
    std = 3
    result = gaussian_pdf(x, mean, std)
    expected_result = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)
    assert np.isclose(result, expected_result, atol=0.01)

    assert abs(result - expected_result) < 0.01


# 5. Test: Fitness Level Probabilities (male, age 30, pushups=25, squats=30)
def test_get_fitness_level_probabilities():
    result = get_fitness_level_probabilities("male", 30, 25, 30)
    assert isinstance(result, dict)
    assert "poor" in result


# 6. Test: Fitness Level Classification
def test_classify_fitness_level():
    result = classify_fitness_level("male", 21, 25, 30)
    expected = "average"  # Based on the provided anchors

    assert result == expected





# 8. Test: Get Training Parameters for Goal (muscle_gain)
def test_get_training_params_for_goal():
    result = get_training_params_for_goal("muscle_gain")
    expected = {'rep_range': (8, 12), 'sets': 3, 'rest_seconds': 90}

    assert result == expected


# 9. Test: Days per Week based on Commitment Level
def test_days_per_week():
    result = days_per_week('medium')
    expected = 4

    assert result == expected


# 10. Test: Get Next Fitness Level
def test_get_next_fitness_level():
    result = get_next_fitness_level("average")
    expected = "above_avg"

    assert result == expected


# 11. Test: Get Difficulty Range for Next Level
def test_get_difficulty_range_for_next_level():
    result = get_difficulty_range_for_next_level("above_avg")
    expected = (3, 4)

    assert result == expected

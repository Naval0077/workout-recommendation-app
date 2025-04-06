import pytest
import os
import json
import numpy as np
from unittest.mock import MagicMock
from app import create_app
from app.models import User, Exercise, Rating
from app.utils.NLP import (
    load_exercise_data,
    build_exercise_text,
    vectorize_exercises_faiss,
    load_faiss_index,
    get_exercise_similarities,
    get_exercise_ratings,
    compute_final_score,
    recommend_exercises_for_goal,
    get_recommendations,
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

# Mock data for testing
mock_exercise_data = [
    {
        "Exercise Name": "Push Up",
        "Main_muscle": "Chest",
        "Target_Muscles": "Chest, Triceps",
        "Synergist_Muscles": "Shoulders",
        "Preparation": "Start in plank position",
        "Execution": "Lower your body and push back up",
        "Difficulty (1-5)": 3,
    },
    {
        "Exercise Name": "Squat",
        "Main_muscle": "Legs",
        "Target_Muscles": "Quadriceps, Hamstrings",
        "Synergist_Muscles": "Glutes",
        "Preparation": "Stand with feet shoulder-width apart",
        "Execution": "Lower your body and rise back up",
        "Difficulty (1-5)": 2,
    },
]

# Test: Build Exercise Text
def test_build_exercise_text():
    ex = mock_exercise_data[0]
    text = build_exercise_text(ex)
    assert "Push Up" in text
    assert "Chest" in text
    assert "Triceps" in text

# Test: Vectorize Exercises FAISS
def test_vectorize_exercises_faiss():
    # Mocking file existence
    if os.path.exists("exercise_faiss.index"):
        os.remove("exercise_faiss.index")
    if os.path.exists("exercise_names.npy"):
        os.remove("exercise_names.npy")

    vectorize_exercises_faiss(mock_exercise_data)
    assert os.path.exists("exercise_faiss.index")
    assert os.path.exists("exercise_names.npy")

# Test: Load FAISS Index
def test_load_faiss_index():
    vectorize_exercises_faiss(mock_exercise_data)
    index, exercise_names = load_faiss_index()

    assert index.is_trained
    assert len(exercise_names) == 2

# Test: Get Exercise Similarities with One-Word Goal
def test_get_exercise_similarities_one_word_goal():
    vectorize_exercises_faiss(mock_exercise_data)
    goal_text = "chest"  # Simpler one-word goal
    similarities = get_exercise_similarities(goal_text)

    assert len(similarities) > 0
    assert "Push Up" in similarities[0][0]  # "Push Up" should be relevant for "chest"

# Test: Get Exercise Ratings
def test_get_exercise_ratings(app, db):
    with app.app_context():
        # Add mock exercises and ratings
        exercise1 = Exercise(name="Push-Up")
        exercise2 = Exercise(name="Squat")
        db.session.add_all([exercise1, exercise2])
        db.session.commit()

        rating1 = Rating(exercise_id=exercise1.id, rating=4, user_id=1)
        rating2 = Rating(exercise_id=exercise1.id, rating=5, user_id=2)
        rating3 = Rating(exercise_id=exercise2.id, rating=3, user_id=3)
        db.session.add_all([rating1, rating2, rating3])
        db.session.commit()

        # Call the function
        ratings = get_exercise_ratings()

        # Ensure the results are as expected
        assert len(ratings) == 2  # Two exercises
        assert ratings["Push-Up"] == 4.5  # Average of 4 and 5 for Push-Up
        assert ratings["Squat"] ==  3.0  # Average of 3 for Squat

# Test: Compute Final Score
def test_compute_final_score():
    similarity = 0.9
    difficulty = 3
    user_difficulty = 2
    rating = 4

    final_score = compute_final_score(similarity, difficulty, user_difficulty, rating)
    assert final_score > 0

# Test: Recommend Exercises for Goal with One-Word Goal
def test_recommend_exercises_for_goal_one_word(app):
    goal_text = "chest"  # Simpler one-word goal
    user_difficulty = 3
    with app.app_context():
        recommended = recommend_exercises_for_goal(mock_exercise_data, goal_text, user_difficulty, top_k=1)

        assert len(recommended) == 1
        assert recommended[0]["Exercise Name"] == "Push Up"  # "Push Up" is related to "chest"

# Test: Get Recommendations with Difficulty Range
def test_get_recommendations_with_difficulty_range(app):
    goal_text = "chest"  # Simpler one-word goal
    min_diff = 2
    max_diff = 3
    with app.app_context():
        recommendations = get_recommendations(mock_exercise_data, goal_text, top_k=2, min_diff=min_diff, max_diff=max_diff)

        assert len(recommendations) > 0
        assert all(min_diff <= int(ex["Difficulty (1-5)"]) <= max_diff for ex in recommendations)

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
        "Exercise Name": "Chest Dip",
        "Equipment": "Assisted",
        "Variation": "No",
        "Utility": "Basic",
        "Mechanics": "Compound",
        "Force": "Push",
        "Preparation": "Mountwide dip barwith oblique grip (bar diagonal under palm), arms straight with shoulders above hands. Step down onto assistance lever with hips and knees bent.",
        "Execution": "Lower body by bending arms, allowing elbows to flare out to sides. When slight stretch is felt in chest or shoulders, push body up until arms are straight. Repeat.",
        "Target_Muscles": "Pectoralis Major Sternal,",
        "Synergist_Muscles": "Deltoid, Anterior, Triceps Brachii, Pectoralis Major, Clavicular, Pectoralis Minor, Rhomboids, Levator Scapulae, Latissimus Dorsi, Teres Major, Coracobrachialis, ",
        "Stabilizer_Muscles": "Trapezius, Lower, ",
        "Antagonist_Muscles": "",
        "Dynamic_Stabilizer_Muscles": "",
        "Main_muscle": "Chest",
        "Difficulty (1-5)": 3,
        "Secondary Muscles": "Triceps Brachii, Anterior Deltoid",
        "parent_id": ""
    },
    {
        "Exercise Name": "Squat",
        "Equipment": "Barbell",
        "Variation": "No",
        "Utility": "Basic",
        "Mechanics": "Compound",
        "Force": "Push",
        "Preparation": "From rack with barbell at upper chest height, position bar low on back of shoulders. Grasp barbell to sides. Dismount bar from rack and stand with wide stance.",
        "Execution": "Squat down by flexing knee and hip of front leg. Allow heel of rear foot to rise up while knee of rear leg bends slightly until it almost makes contact with floor. Return to original standing position by extending hip and knee of forward leg. Repeat. Continue with opposite leg.",
        "Target_Muscles": "Gluteus Maximus,",
        "Synergist_Muscles": "Quadriceps, Adductor Magnus, Soleus, ",
        "Stabilizer_Muscles": "Erector Spinae, ",
        "Antagonist_Muscles": "Rectus Abdominis, Obliques, ",
        "Dynamic_Stabilizer_Muscles": "Hamstrings, Gastrocnemius, ",
        "Main_muscle": "Hips",
        "Difficulty (1-5)": 4,
        "Secondary Muscles": "Quadriceps, Gluteus Maximus, Adductors",
        "parent_id": ""
    },
]

# Test: Build Exercise Text
def test_build_exercise_text():
    ex = mock_exercise_data[0]
    text = build_exercise_text(ex)
    assert "Chest" in text


# Test: Load FAISS Index
def test_load_faiss_index():
    index, exercise_names = load_faiss_index()

    assert index.is_trained
    assert len(exercise_names) > 0

# Test: Get Exercise Similarities with One-Word Goal
def test_get_exercise_similarities_one_word_goal():
    goal_text = "chest"  # Simpler one-word goal
    similarities = get_exercise_similarities(goal_text)

    assert len(similarities) > 0

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

# Test: Get Recommendations with Difficulty Range
def test_get_recommendations_with_difficulty_range(app):
    goal_text = "chest"  # Simpler one-word goal
    min_diff = 2
    max_diff = 3
    with app.app_context():
        recommendations = get_recommendations(mock_exercise_data, goal_text, top_k=2, min_diff=min_diff, max_diff=max_diff)

        assert len(recommendations) > 0
        assert all(min_diff <= int(ex["Difficulty (1-5)"]) <= max_diff for ex in recommendations)

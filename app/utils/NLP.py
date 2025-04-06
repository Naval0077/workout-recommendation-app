import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from sqlalchemy import func
from app import db
from app.models import Exercise, Rating

# Paths to stored FAISS index and exercise metadata
FAISS_INDEX_PATH = "exercise_faiss.index"
EXERCISE_NAMES_PATH = "exercise_names.npy"

# Load the Sentence-BERT model
model = SentenceTransformer("all-MiniLM-L6-v2")  # Efficient and fast


# Load exercise metadata
def load_exercise_data(json_file):
    with open(json_file, "r") as f:
        return json.load(f)


# Build a text representation for each exercise
def build_exercise_text(ex):
    fields = [
        ex.get('Exercise Name', ''),
        ex.get('Main_muscle', ''),
        ex.get('Target_Muscles', ''),
        ex.get('Synergist_Muscles', ''),
        ex.get('Preparation', ''),
        ex.get('Execution', '')
    ]
    return " ".join(fields)


# Function to vectorize exercises and store them in FAISS index
def vectorize_exercises_faiss(exercises):
    # Check if FAISS index already exists. If it does, skip the vectorization
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(EXERCISE_NAMES_PATH):
        print("🔄 FAISS index already exists. Skipping vectorization.")
        return

    print("⚡ Vectorizing exercises and creating FAISS index...")

    # Generate text representations for the exercises
    exercise_texts = [build_exercise_text(ex) for ex in exercises]

    # Generate embeddings for the exercises using Sentence-BERT
    exercise_embeddings = model.encode(exercise_texts, convert_to_numpy=True, normalize_embeddings=True)

    # Create the FAISS index using inner product (cosine similarity)
    embedding_dim = exercise_embeddings.shape[1]
    index = faiss.IndexFlatIP(embedding_dim)  # Use inner product (cosine similarity)

    # Add the embeddings to the FAISS index
    index.add(exercise_embeddings)

    # Save the FAISS index and exercise names
    faiss.write_index(index, FAISS_INDEX_PATH)
    np.save(EXERCISE_NAMES_PATH, np.array([ex["Exercise Name"] for ex in exercises]))

    print("✅ FAISS index and exercise names saved successfully!")

# Load FAISS index and exercise names
def load_faiss_index():
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(EXERCISE_NAMES_PATH):
        raise RuntimeError("🚨 FAISS index or exercise names not found! Run vectorization first.")

    index = faiss.read_index(FAISS_INDEX_PATH)
    exercise_names = np.load(EXERCISE_NAMES_PATH, allow_pickle=True)

    return index, exercise_names


# Retrieve similarity scores for the goal text
def get_exercise_similarities(goal_text, top_k=50):
    index, exercise_names = load_faiss_index()

    # Encode the goal text using SBERT
    goal_vector = model.encode([goal_text], convert_to_numpy=True, normalize_embeddings=True)

    # Search for the most similar exercises
    scores, indices = index.search(goal_vector, top_k)

    return [(exercise_names[i], scores[0][j]) for j, i in enumerate(indices[0])]


# Fetch average ratings from database
def get_exercise_ratings():
    ratings_query = (
        db.session.query(Exercise.name, func.avg(Rating.rating).label("avg_rating"))
        .join(Rating)
        .group_by(Exercise.id)
        .all()
    )
    return {name: round(avg_rating, 2) for name, avg_rating in ratings_query}


# Compute final recommendation score (similarity + difficulty + rating)
def compute_final_score(similarity, difficulty, user_difficulty, rating, alpha=1.0, beta=0.3, gamma=0.1):
    difficulty_penalty = abs(difficulty - user_difficulty) * beta
    rating_bonus = (rating - 3) * gamma
    return (alpha * similarity) - difficulty_penalty + rating_bonus


# Recommend exercises based on user goal
def recommend_exercises_for_goal(exercises, goal_text, user_difficulty, top_k):
    similarities = get_exercise_similarities(goal_text)
    ratings = get_exercise_ratings()

    # Compute final scores considering similarity & difficulty
    recommended_exercises = []
    for exercise_name, similarity in similarities:
        exercise = next((e for e in exercises if e["Exercise Name"] == exercise_name), None)
        if not exercise:
            continue

        difficulty = int(exercise.get("Difficulty (1-5)", 3))  # Default to 3 if missing
        rating = ratings.get(exercise_name, 3.0)
        final_score = compute_final_score(similarity, difficulty, user_difficulty, rating)

        exercise_copy = exercise.copy()
        exercise_copy["score"] = final_score
        recommended_exercises.append(exercise_copy)

    # Sort by final score
    recommended_exercises.sort(key=lambda x: x["score"], reverse=True)
    print(recommended_exercises[:top_k])

    return recommended_exercises[:top_k]


# Get workout recommendations with difficulty range
def get_recommendations(exercise_data, goal_text, top_k, min_diff, max_diff):
    # Get recommendations for both min and max difficulty
    vectorize_exercises_faiss(exercise_data)
    goal_recommendations_min = recommend_exercises_for_goal(exercise_data, goal_text, min_diff, top_k)
    goal_recommendations_max = recommend_exercises_for_goal(exercise_data, goal_text, max_diff, top_k)

    # Combine and remove duplicates
    seen = set()
    unique_recommendations = []
    for exercise in goal_recommendations_min + goal_recommendations_max:
        if exercise["Exercise Name"] not in seen:
            seen.add(exercise["Exercise Name"])
            unique_recommendations.append(exercise)

    return unique_recommendations

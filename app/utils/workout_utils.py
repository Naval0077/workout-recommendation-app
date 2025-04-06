import json
import math
import random

import joblib
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from app.models import User
from app import db

import json

# Load exercise priors from a JSON file
import numpy as np
from scipy.stats import norm

from app.utils.NLP import get_recommendations

# Define fitness levels
fitness_levels = ['Poor', 'Below Average', 'Average', 'Above Average', 'Excellent']

# Naive prior probabilities (e.g., 50% for Average)
naive_priors = {
    'poor':       0.05,
    'below_avg':  0.15,
    'average':    0.50,
    'above_avg':  0.20,
    'excellent':  0.10
}


# def generate_workouts(user):
#     # Prepare user data for prediction
#     model = joblib.load('app/ml/workout_model.pkl')
#     user_data = pd.DataFrame({
#         'height': [user.height],
#         'weight': [user.weight],
#         'pushups': [user.pushups],
#         'squats': [user.squats],
#         'plank_time': [user.plank_time],
#         'goal': [goal_mapping[user.goal]],  # Encode 'goal'
#         'commitment': [commitment_mapping[user.commitment]]
#     })
#
#     # Debug: Print user data
#     print("User data for prediction:")
#     print(user_data)
#
#     # Predict workout category
#     category_id = model.predict(user_data)[0]
#     categories = {0: 'Cardio', 1: 'Strength', 2: 'HIIT'}
#     category = categories[category_id]
#     print(category_id)
#
#     # Filter workouts based on predicted category
#     recommended_workouts = [w for w in workout_db['workouts'] if w['workout_category'] == category]
#
#     feedback = Feedback.query.filter_by(user_id=user.id).first()
#     if feedback:
#         new_data = {
#             'height': user.height,
#             'weight': user.weight,
#             'pushups': user.pushups,
#             'situps': user.situps,
#             'plank_time': user.plank_time,
#             'goal': user.goal,
#             'commitment': user.commitment,
#             'workout_category': feedback.workout_id  # Use feedback to determine the correct category
#         }
#
#         # Load existing training data
#         try:
#             existing_data = pd.read_csv('app/data/workout_data.csv')
#         except FileNotFoundError:
#             existing_data = pd.DataFrame()
#
#         # Append new data
#         new_data_df = pd.DataFrame([new_data])
#         combined_data = pd.concat([existing_data, new_data_df], ignore_index=True)
#
#         # Encode categorical variables
#         combined_data['goal'] = combined_data['goal'].map({'weight_loss': 0, 'muscle_gain': 1, 'endurance': 2})
#         combined_data['commitment'] = combined_data['commitment'].map({'low': 0, 'medium': 1, 'high': 2})
#         combined_data['workout_category'] = combined_data['workout_category'].map({0: 0, 1: 1, 2: 2})
#
#         # Features and target
#         X = combined_data.drop('workout_category', axis=1)
#         y = combined_data['workout_category']
#
#         # Retrain the model
#         model = DecisionTreeClassifier()
#         model.fit(X, y)
#
#         # Save the updated model
#         joblib.dump(model, 'app/ml/workout_model.pkl')
#
#         # Save the updated dataset
#         combined_data.to_csv('app/data/workout_data.csv', index=False)
#
#     print("Recommended workouts:")
#     print(recommended_workouts)
#     return recommended_workouts

#
# def adjust_priors_for_goal(category_priors, goal):
#     if goal == 'weight_loss':
#         category_priors['Cardio'] *= 1.5  # Increase priority for cardio
#     elif goal == 'muscle_gain':
#         category_priors['Upper Body'] *= 1.5  # Increase priority for upper body
#         category_priors['Lower Body'] *= 1.5  # Increase priority for lower body
#     elif goal == 'endurance':
#         category_priors['Cardio'] *= 1.5  # Increase priority for cardio
#         category_priors['Core'] *= 1.2  # Slightly increase priority for core
#
#     # Normalize the probabilities
#     total = sum(category_priors.values())
#     for category in category_priors:
#         category_priors[category] /= total
#
#     return category_priors
#

# Push-up data for Male and Female by age group
# buffer  =10
# push_up_data = {
#     'Male': {
#         '15-19': {'Poor': (0, 17), 'Below Average': (18, 22), 'Average': (23, 28), 'Above Average': (29, 38), 'Excellent': (39, 39+buffer)},
#         '20-29': {'Poor': (0, 16), 'Below Average': (17, 21), 'Average': (22, 28), 'Above Average': (29, 35), 'Excellent': (36, 36+buffer)},
#         '30-39': {'Poor': (0, 11), 'Below Average': (12, 16), 'Average': (17, 21), 'Above Average': (22, 29), 'Excellent': (30, 30+buffer)},
#         '40-49': {'Poor': (0, 9), 'Below Average': (10, 12), 'Average': (13, 16), 'Above Average': (17, 21), 'Excellent': (22, 22+buffer)},
#         '50-59': {'Poor': (0, 6), 'Below Average': (7, 9), 'Average': (10, 12), 'Above Average': (13, 20),'Excellent': (21, 21+buffer)},
#         '60-69': {'Poor': (0, 4), 'Below Average': (5, 7), 'Average': (8, 10), 'Above Average': (11, 17),'Excellent': (18, 18+buffer)},
#
#     },
#     'Female': {
#         '15-19': {'Poor': (0, 11), 'Below Average': (12, 17), 'Average': (18, 24), 'Above Average': (25, 32), 'Excellent': (33, 33+buffer)},
#         '20-29': {'Poor': (0, 9), 'Below Average': (10, 14), 'Average': (15, 20), 'Above Average': (21, 29), 'Excellent': (30, 30+buffer)},
#         '30-39': {'Poor': (0, 7), 'Below Average': (8, 12), 'Average': (13, 19), 'Above Average': (20, 26), 'Excellent': (27, 27+buffer)},
#         '40-49': {'Poor': (0, 4), 'Below Average': (5, 10), 'Average': (11, 14), 'Above Average': (15, 23), 'Excellent': (24, 24+buffer)},
#         '50-59': {'Poor': (0, 1), 'Below Average': (2, 6), 'Average': (7, 10), 'Above Average': (11, 20), 'Excellent': (21, 21+buffer)},
#         '60-69': {'Poor': (0, 1), 'Below Average': (2, 4), 'Average': (5, 11), 'Above Average': (12, 17), 'Excellent': (18, 18+buffer)},
#     }
# }
#
# # Squat data for Male and Female by age group
# squat_data = {
#     'Male': {
#         '20-29': { 'Poor': (0, 23), 'Below Average': (24, 26), 'Average': (27, 29), 'Above Average': (30, 32), 'Excellent': (33, 33+buffer)},
#         '30-39': { 'Poor': (0, 20), 'Below Average': (21, 23), 'Average': (24, 26), 'Above Average': (27, 29), 'Excellent': (30, 30+buffer)},
#         '40-49': {'Poor': (0, 17), 'Below Average': (18, 20), 'Average': (21, 23), 'Above Average': (24, 26), 'Excellent': (27, 27+buffer)},
#         '50-59': {'Poor': (0, 14), 'Below Average': (15, 17), 'Average': (18, 20), 'Above Average': (21, 23), 'Excellent': (24, 24+buffer)},
#         '60-69': {'Poor': (0, 11), 'Below Average': (12, 14), 'Average': (15, 17), 'Above Average': (18, 20), 'Excellent': (21, 21+buffer)},
#     },
#     'Female': {
#         '20-29': {'Poor': (0, 17), 'Below Average': (18, 20), 'Average': (21, 23), 'Above Average': (24, 26), 'Excellent': (27, 27+buffer)},
#         '30-39': {'Poor': (0, 14), 'Below Average': (15, 17), 'Average': (18, 20), 'Above Average': (21, 23), 'Excellent': (23, 23+buffer)},
#         '40-49': {'Poor': (0, 11), 'Below Average': (12, 14), 'Average': (15, 17), 'Above Average': (18, 20), 'Excellent': (21, 21+buffer)},
#         '50-59': {'Poor': (0, 8), 'Below Average': (9, 11), 'Average': (12, 14), 'Above Average': (15, 17), 'Excellent': (18, 18+buffer)},
#         '60-69': {'Poor': (0, 5), 'Below Average': (6, 8), 'Average': (9, 11), 'Above Average': (12, 14), 'Excellent': (15, 15+buffer)},
#     }
# }
# A helper to map actual age into one of the bucket strings in the dictionary
import math
import bisect

##############################################################################
# 1) ANCHOR DATA: Means at certain ages for Men/Women, Pushups/Squats, 5 Levels
##############################################################################

men_pushup_anchors = {
    'poor': [(20, 14), (30, 10), (40, 8), (50, 5), (60, 3)],
    'below_avg': [(20, 19), (30, 14), (40, 11), (50, 8), (60, 6)],
    'average': [(20, 25), (30, 19), (40, 15), (50, 11), (60, 9)],
    'above_avg': [(20, 32), (30, 26), (40, 19), (50, 17), (60, 14)],
    'excellent': [(20, 40), (30, 34), (40, 26), (50, 24), (60, 20)]
}

men_squat_anchors = {
    'poor': [(20, 22), (30, 19), (40, 16), (50, 13), (60, 10)],
    'below_avg': [(20, 25), (30, 22), (40, 19), (50, 16), (60, 13)],
    'average': [(20, 28), (30, 25), (40, 22), (50, 19), (60, 16)],
    'above_avg': [(20, 31), (30, 28), (40, 25), (50, 22), (60, 19)],
    'excellent': [(20, 37), (30, 35), (40, 33), (50, 29), (60, 27)]
}

women_pushup_anchors = {
    'poor': [(20, 7), (30, 5), (40, 3), (50, 2), (60, 1)],
    'below_avg': [(20, 12), (30, 10), (40, 7), (50, 4), (60, 3)],
    'average': [(20, 18), (30, 16), (40, 12), (50, 8), (60, 6)],
    'above_avg': [(20, 25), (30, 23), (40, 19), (50, 14), (60, 12)],
    'excellent': [(20, 34), (30, 31), (40, 26), (50, 22), (60, 18)]
}

women_squat_anchors = {
    'poor': [(20, 16), (30, 13), (40, 9), (50, 7), (60, 4)],
    'below_avg': [(20, 19), (30, 15), (40, 12), (50, 9), (60, 6)],
    'average': [(20, 22), (30, 18), (40, 15), (50, 10), (60, 8)],
    'above_avg': [(20, 25), (30, 23), (40, 20), (50, 15), (60, 12)],
    'excellent': [(20, 32), (30, 28), (40, 24), (50, 20), (60, 17)]
}

FITNESS_LEVELS = ['poor', 'below_avg', 'average', 'above_avg', 'excellent']


##############################################################################
# 2) LINEAR INTERPOLATION HELPER
##############################################################################

def linear_interpolate(x, xp, fp):
    """
    Given a value x, and parallel lists xp (anchor x-values) and fp (anchor f-values),
    perform linear interpolation. xp and fp must be sorted by xp.
    """
    # If x is below/above the anchor range, clamp to endpoints
    if x <= xp[0]:
        return fp[0]
    if x >= xp[-1]:
        return fp[-1]

    # Find the interval via bisect
    i = bisect.bisect_left(xp, x) - 1
    # Linear interpolation
    x0, x1 = xp[i], xp[i + 1]
    f0, f1 = fp[i], fp[i + 1]
    return f0 + (f1 - f0) * ((x - x0) / (x1 - x0))


##############################################################################
# 3) GET MEAN & STD FOR A GIVEN (gender, age, fitness_level) FOR PUSHUPS/SQUATS
##############################################################################

def get_mean_pushups(gender, age, level):
    """
    Return the interpolated mean pushups for the given gender, age, and fitness level.
    """
    if gender.lower() == 'male':
        anchors = men_pushup_anchors[level]
    else:
        anchors = women_pushup_anchors[level]
    anchor_ages = [pt[0] for pt in anchors]
    anchor_means = [pt[1] for pt in anchors]
    return linear_interpolate(age, anchor_ages, anchor_means)


def get_mean_squats(gender, age, level):
    """
    Return the interpolated mean squats for the given gender, age, and fitness level.
    """
    if gender.lower() == 'male':
        anchors = men_squat_anchors[level]
    else:
        anchors = women_squat_anchors[level]
    anchor_ages = [pt[0] for pt in anchors]
    anchor_means = [pt[1] for pt in anchors]
    return linear_interpolate(age, anchor_ages, anchor_means)


def get_std_pushups(gender, age, level):
    """
    Example: standard deviation might increase slightly with age.
    We'll do a simple linear interpolation from (age=20 -> std=3) to (age=60 -> std=5).
    You can refine this logic or vary it by fitness level.
    """
    anchor_ages = [20, 60]
    anchor_stds = [3, 5]
    return linear_interpolate(age, anchor_ages, anchor_stds)


def get_std_squats(gender, age, level):
    """
    Same approach for squats: let's do the same range of std=3 to std=5 from age 20 to 60.
    """
    anchor_ages = [20, 60]
    anchor_stds = [3, 5]
    return linear_interpolate(age, anchor_ages, anchor_stds)


##############################################################################
# 4) GAUSSIAN PDF
##############################################################################

def gaussian_pdf(x, mean, std):
    """
    Evaluate the probability density function of a normal distribution
    with given mean and std at point x.
    """
    if std <= 0:
        return 0.0
    factor = 1.0 / (math.sqrt(2 * math.pi) * std)
    exponent = math.exp(-0.5 * ((x - mean) / std) ** 2)
    return factor * exponent


##############################################################################
# 5) FUNCTION: GET THE LIKELIHOOD P(PUSHUPS=p, SQUATS=q | F=f, AGE=a)
#    BUT IF YOU JUST WANT P(PUSHUPS=p | F=f, AGE=a) & P(SQUATS=q | F=f, AGE=a),
#    YOU CAN RETURN THOSE SEPARATELY AS WELL.
##############################################################################

def get_fitness_level_probabilities(gender, age, pushups, squats):
    """
    Returns a dictionary mapping each fitness level -> (pPushups, pSquats, product)
    i.e. the Gaussian likelihood for pushups, squats, and their product (Naive Bayes style).

    This is NOT a posterior probability yet (no prior is multiplied),
    but it shows how likely each level's distribution is for the given pushups & squats.
    """
    results = {}
    for level in FITNESS_LEVELS:
        mu_p = get_mean_pushups(gender, age, level)
        sd_p = get_std_pushups(gender, age, level)
        p_push = gaussian_pdf(pushups, mu_p, sd_p)

        mu_q = get_mean_squats(gender, age, level)
        sd_q = get_std_squats(gender, age, level)
        p_squat = gaussian_pdf(squats, mu_q, sd_q)

        # If you want the naive Bayes product (assuming P & Q conditionally independent):
        product = p_push * p_squat

        results[level] =  (p_push, p_squat, product)

    return results

def classify_fitness_level(gender, age, pushups, squats):
    products = get_fitness_level_probabilities(gender, age, pushups, squats)
    posterior_sum = 0.0
    posteriors = {}
    for level, (pPush, pSquat, product) in products.items():
        unnormalized = product * naive_priors[level]
        posteriors[level] = unnormalized
        posterior_sum += unnormalized

    for level in FITNESS_LEVELS:
        posteriors[level] /= (posterior_sum + 1e-12)  # to avoid divide by zero

    best_level = max(posteriors, key=posteriors.get)
    return best_level

# print(classify_fitness_level("male", 21, 25, 30))




import random

def get_training_params_for_goal(goal):
    goal = goal.lower()
    if goal == 'muscle_gain':
        return {
            'rep_range': (8, 12),
            'sets': 3,
            'rest_seconds': 90
        }
    elif goal == 'endurance':
        return {
            'rep_range': (12, 20),
            'sets': 2,
            'rest_seconds': 60
        }
    elif goal == 'weight_loss':
        return {
            'rep_range': (10, 15),
            'sets': 3,
            'rest_seconds': 45
        }
    else:
        # default
        return {
            'rep_range': (8, 12),
            'sets': 3,
            'rest_seconds': 90
        }
def days_per_week(commitment_level):

    if commitment_level == 'low':
        return 2
    elif commitment_level == 'medium':
        return 4
    elif commitment_level == 'high':
        return 5
    else:
        return 3  # default

def get_next_fitness_level(current_level):
    order = ['poor','below_avg','average','above_avg','excellent']
    idx = order.index(current_level)
    if idx == len(order) - 1:
        return 'excellent'
    else:
        return order[idx + 1]

def get_difficulty_range_for_next_level(next_level):
    mapping = {
        'below_avg':  (1, 2),
        'average':    (2, 3),
        'above_avg':  (3, 4),
        'excellent':  (4, 5)
    }
    # If not in the dict (e.g. already excellent), just pick 3-5
    return mapping.get(next_level, (3, 5))
import json

def load_exercises(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data



def build_workout_schedule(exercise, gender, age, pushups, squats, commitment, goal, daily_goals):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    current_level = classify_fitness_level(gender, age, pushups, squats)
    next_level = get_next_fitness_level(current_level)

    min_diff, max_diff = get_difficulty_range_for_next_level(next_level)

    training_params = get_training_params_for_goal(goal)
    rep_range = training_params['rep_range']
    sets = training_params['sets']
    rest = training_params['rest_seconds']

    schedule = {day: [] for day in days}
    selected_exercises = set()
    num = 0

    for day in days:  # Only generate workouts for selected days
        if day not in daily_goals:
            continue  # Skip unused days

        muscles = daily_goals[day]  # 🚀 Get muscle groups selected by the user
        day_exercises = []

        # Add exercises for each muscle group
        for muscle in muscles:
            num = num+1
            unique_exercises = set()
            goal_text = f"{muscle} muscles"
            filtered = get_recommendations(exercise, goal_text, 10, min_diff, max_diff)

            while len(unique_exercises) < 2 and filtered:
                ex = random.choice(filtered)

                if ex["Exercise Name"] not in selected_exercises:
                    day_exercises.append(ex)
                    selected_exercises.add(ex["Exercise Name"])
                    unique_exercises.add(ex["Exercise Name"])

        # Store the final day plan
        for ex in day_exercises:
            ex_entry = {
                "Exercise Name": ex["Exercise Name"],
                "Difficulty": ex["Difficulty (1-5)"],
                "Muscle": ex["Main_muscle"],
                "Sets": sets,
                "Reps": f"{rep_range[0]}-{rep_range[1]}",  # e.g. "8-12"
                "Rest (seconds)": rest,
                "Equipment": ex["Equipment"],
                "Preparation": ex["Preparation"],
                "Execution": ex["Execution"]
            }
            schedule[day].append(ex_entry)

    return schedule



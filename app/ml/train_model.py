import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

# Load training data
data = pd.read_csv('app/data/workout_data.csv')

# Check for missing values
print("Missing values before handling:")
print(data.isnull().sum())

# Standardize categorical values
data['goal'] = data['goal'].str.strip().str.lower()
data['commitment'] = data['commitment'].str.strip().str.lower()
data['workout_category'] = data['workout_category'].str.strip().str.lower()

# Replace variations with standardized values
data['goal'] = data['goal'].replace({
    'weight loss': 'weight_loss',
    'muscle gain': 'muscle_gain'
})

data['commitment'] = data['commitment'].replace({
    'low commitment': 'low',
    'medium commitment': 'medium',
    'high commitment': 'high'
})

data['workout_category'] = data['workout_category'].replace({
    'cardioo': 'cardio',
    'strength training': 'strength',
    'hiit workout': 'hiit'
})

# Encode categorical variables
data['goal'] = data['goal'].map({'weight_loss': 0, 'muscle_gain': 1, 'endurance': 2})
data['commitment'] = data['commitment'].map({'low': 0, 'medium': 1, 'high': 2})
data['workout_category'] = data['workout_category'].map({'cardio': 0, 'strength': 1, 'hiit': 2})

# Check for NaN values after encoding
print("NaN values after encoding:")
print(data.isnull().sum())

# Handle NaN values
if data.isnull().any().any():
    print("Handling NaN values...")
    data = data.dropna()  # Drop rows with NaN values
    # OR
    # data['workout_category'] = data['workout_category'].fillna(0)  # Default to 'Cardio'

# Features and target
X = data.drop('workout_category', axis=1)
y = data['workout_category']

# Check for NaN in y
if y.isnull().any():
    print("NaN values found in y:")
    print(y[y.isnull()])
    # Handle NaN in y (e.g., drop or fill)
    y = y.dropna()
    X = X.loc[y.index]  # Ensure X and y have the same rows

# Train the model
model = DecisionTreeClassifier()
model.fit(X, y)

# Save the model
joblib.dump(model, 'app/ml/workout_model.pkl')
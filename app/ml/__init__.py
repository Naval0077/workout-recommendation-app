# Import the trained model to make it available when the package is imported
import joblib

# Load the trained model
model = joblib.load('app/ml/workout_model.pkl')

# Optional: Define any package-level variables or configurations
# For example:
# MODEL_VERSION = '1.0'
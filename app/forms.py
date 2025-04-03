from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, TextAreaField, SubmitField, PasswordField
from wtforms.fields.choices import SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo

class UserInputForm(FlaskForm):
    height = FloatField('Height (in cm)', validators=[DataRequired()])
    weight = FloatField('Weight (in kg)', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')],validators=[DataRequired()])
    pushups = IntegerField('Number of Pushups', validators=[DataRequired()])
    squats = IntegerField('Number of Squats', validators=[DataRequired()])
    plank_time = FloatField('Plank Time (in seconds)', validators=[DataRequired()])
    goal = SelectField('Goal', choices=[('weight_loss', 'Weight Loss'), ('muscle_gain', 'Muscle Gain'), ('endurance', 'Endurance')], validators=[DataRequired()])
    commitment = SelectField('Commitment', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], validators=[DataRequired()])
    submit = SubmitField('Get Recommendations')

class FeedbackForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired()])
    comments = TextAreaField('Comments')
    submit = SubmitField('Submit Feedback')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class WorkoutForm(FlaskForm):
    name = StringField('Workout Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Upper Body', 'Upper Body'),
        ('Lower Body', 'Lower Body'),
        ('Core', 'Core'),
        ('Cardio', 'Cardio')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Workout')


class FitnessTestForm(FlaskForm):
    pushups = IntegerField("Push-Up Count", validators=[DataRequired()])
    squats = IntegerField("Squat Count", validators=[DataRequired()])
    new_fitness_level = StringField("New Fitness Level", render_kw={'readonly': True})  # Changed to StringField
    submit = SubmitField("Submit Test Results")


MUSCLE_GROUPS = [
    ('chest', 'Chest'), ('triceps', 'Triceps'), ('back', 'Back'),
    ('biceps', 'Biceps'), ('legs', 'Legs'), ('shoulders', 'Shoulders'), ('abs', 'Abs')
]


class WorkoutSelectionForm(FlaskForm):
    monday = SelectMultipleField('Monday', choices=MUSCLE_GROUPS, validators=[DataRequired()])
    tuesday = SelectMultipleField('Tuesday', choices=MUSCLE_GROUPS, validators=[DataRequired()])
    wednesday = SelectMultipleField('Wednesday', choices=MUSCLE_GROUPS, validators=[DataRequired()])
    thursday = SelectMultipleField('Thursday', choices=MUSCLE_GROUPS, validators=[DataRequired()])
    friday = SelectMultipleField('Friday', choices=MUSCLE_GROUPS, validators=[DataRequired()])
    saturday = SelectMultipleField('Saturday', choices=MUSCLE_GROUPS, validators=[DataRequired()])
    sunday = SelectMultipleField('Sunday', choices=MUSCLE_GROUPS, validators=[DataRequired()])

    submit = SubmitField('Generate Workout Plan')
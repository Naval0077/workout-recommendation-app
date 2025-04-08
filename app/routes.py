import json

from flask import Blueprint, render_template, redirect, url_for, flash, Response, jsonify, request
from flask_login import login_user, current_user, login_required, logout_user

from app.forms import UserInputForm, FeedbackForm, RegistrationForm, LoginForm, WorkoutForm, FitnessTestForm, \
    WorkoutSelectionForm
from app.models import User, Rating, UserProfile, Exercise, WorkoutPreferences
from app.squats import generate_squats_frames, get_squats_count
from app.utils.workout_utils import (build_workout_schedule, classify_fitness_level)
from app import db
from app.pushups import generate_frames, get_pushup_count
import os


base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
file_path = os.path.join(base_path, 'workouts.json')
main = Blueprint('main', __name__)


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.input'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if form.validate_on_submit():
            # Check if passwords match
            if form.password.data != form.confirm_password.data:
                flash('Passwords must match.', 'danger')
                return render_template('register.html', form=form)

        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('main.login'))  # Redirect to login page
        user = User(email=form.email.data)
        user.set_password(form.password.data) # fix probably
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please complete your profile.', 'success')
        login_user(user)  # Log the user in after registration
        return redirect(url_for('main.input'))  # Redirect to profile setup
    return render_template('register.html', form=form)

@main.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.input'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@main.route('/input', methods=['GET', 'POST'])
@login_required
def input():
    form = UserInputForm()
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()

    if form.validate_on_submit():
        print(f"Gender: {form.gender.data}")
        print(f"Goal: {form.goal.data}")
        print(f"Commitment: {form.commitment.data}")
        count = get_pushup_count()
        print("Form submitted with data:", form.data)  # Debug: Print form data
        try:
            if user_profile:
                # Update existing profile
                user_profile.height = form.height.data
                user_profile.weight = form.weight.data
                user_profile.age = form.age.data
                user_profile.gender = form.gender.data
                user_profile.pushups = form.pushups.data
                user_profile.squats = form.squats.data
                user_profile.plank_time = form.plank_time.data
                user_profile.goal = form.goal.data
                user_profile.commitment = form.commitment.data
                user_profile.fitness_level = classify_fitness_level(user_profile.gender, user_profile.age, user_profile.pushups, user_profile.squats)
            else:
                # Create a new profile
                user_profile = UserProfile(
                    user_id=current_user.id,
                    height=form.height.data,
                    weight=form.weight.data,
                    age=form.age.data,
                    gender=form.gender.data,
                    pushups=form.pushups.data,
                    squats=form.squats.data,
                    plank_time=form.plank_time.data,
                    goal=form.goal.data,
                    commitment=form.commitment.data
                )
                db.session.add(user_profile)
            print(user_profile.fitness_level)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.customize_workout', user_id=current_user.id))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    else:
        print("Form errors:", form.errors)  # Debug: Print form validation errors

    # Prefill the form if the user profile exists
    if user_profile:
        form.height.data = user_profile.height
        form.weight.data = user_profile.weight
        form.age.data = user_profile.age
        form.gender.data = user_profile.gender
        form.pushups.data = user_profile.pushups
        form.squats.data = user_profile.squats
        form.plank_time.data = user_profile.plank_time
        form.goal.data = user_profile.goal
        form.commitment.data = user_profile.commitment

    return render_template('input.html', form=form)

from flask import session


@main.route('/schedule')
@login_required
def schedule():
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    workout_pref = WorkoutPreferences.query.filter_by(user_id=current_user.id).first()
    if not workout_pref:
        flash('Please customize your workout first.', 'warning')
        return redirect(url_for('main.customize_workout'))
    if user_profile:
        try:
            # Try to open the file and load data
            with open(file_path, "r") as f:
                exercises = json.load(f)

            daily_goals = {
                "Monday": workout_pref.monday.split(",") if workout_pref.monday else [],
                "Tuesday": workout_pref.tuesday.split(",") if workout_pref.tuesday else [],
                "Wednesday": workout_pref.wednesday.split(",") if workout_pref.wednesday else [],
                "Thursday": workout_pref.thursday.split(",") if workout_pref.thursday else [],
                "Friday": workout_pref.friday.split(",") if workout_pref.friday else [],
                "Saturday": workout_pref.saturday.split(",")if workout_pref.saturday else [],
                "Sunday": workout_pref.sunday.split(",") if workout_pref.sunday else [],
            }

            weekly_schedule = build_workout_schedule(
                exercise=exercises,
                gender=user_profile.gender,
                age=user_profile.age,
                pushups=user_profile.pushups,
                squats=user_profile.squats,
                commitment=user_profile.commitment,
                goal=user_profile.goal,
                daily_goals=daily_goals,
            )

            # Add exercises to the database if not already added
            for day, exercises_in_day in weekly_schedule.items():
                for exercise_data in exercises_in_day:
                    add_exercise_if_not_exists(exercise_data)

            # Get all exercises and calculate average ratings
            exercises = Exercise.query.all()
            exercise_ratings = {}
            for exercise in exercises:
                ratings = Rating.query.filter_by(exercise_id=exercise.id).all()

                if ratings:
                    avg_rating = sum([rating.rating for rating in ratings]) / len(ratings)
                    exercise_ratings[exercise.name] = {
                        'avg_rating': float(avg_rating),
                        'rating_count': len(ratings)
                    }
                else:
                    exercise_ratings[exercise.name] = {
                        'avg_rating': 'No ratings yet',
                        'rating_count': 0
                    }

            return render_template('schedule.html', schedule=weekly_schedule, exercise_ratings=exercise_ratings)

        except FileNotFoundError:
            flash(f"Could not find the workouts.json file at {file_path}. Please check the file path.", 'danger')
            return redirect(url_for('main.input'))

    else:
        flash('Please complete your profile to view the schedule.', 'warning')
        return redirect(url_for('main.input'))



@main.route('/rate_exercise/<exercise_name>', methods=['POST'])
def rate_exercise(exercise_name):
    rating_value = float(request.form['rating'])
    user_id = current_user.id
    exercise = Exercise.query.filter_by(name=exercise_name).first()


    # Check if the user has already rated this exercise
    existing_rating = Rating.query.filter_by(user_id=user_id, exercise_id=exercise.id).first()

    if existing_rating:
        flash('You have already rated this exercise!', 'warning')
        return redirect(url_for('main.schedule'))  # Redirect to the schedule page or wherever you need

    # If not, create a new rating
    new_rating = Rating(exercise_id=exercise.id, rating=rating_value, user_id=user_id)
    db.session.add(new_rating)
    db.session.commit()

    flash('Your rating has been submitted!', 'success')
    return redirect(url_for('main.schedule'))

# Route to display average ratings
@main.route('/exercise_ratings/<exercise_name>')
def exercise_ratings(exercise_name):
    exercise = Exercise.query.filter_by(name=exercise_name).first()

    if exercise:
        ratings = Rating.query.filter_by(exercise_id=exercise.id).all()
        total_ratings = len(ratings)
        avg_rating = sum(r.rating for r in ratings) / total_ratings if total_ratings > 0 else 0
        return render_template('ratings.html', exercise=exercise, avg_rating=avg_rating, total_ratings=total_ratings)
    else:
        return "Exercise not found!"




@main.route('/logout')
@login_required
def logout():
    session.pop("weekly_schedule", None)
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('main.login'))

@main.route("/pushup_feed")
def pushup_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@main.route("/squats_feed")
def squats_feed():
    return Response(generate_squats_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@main.route("/save_squats", methods=["POST"])
@login_required
def save_squats():
    count = get_squats_count()

    # Save push-up count to database
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if user_profile:
        user_profile.squats = count
    else:
        user_profile = UserProfile(user_id=current_user.id, squats=count)
        db.session.add(user_profile)

    db.session.commit()
    db.session.flush()  # Force immediate database sync
    return jsonify({"message": "Squats saved!", "count": count})


@main.route("/save_pushups", methods=["POST"])
@login_required
def save_pushups():
    count = get_pushup_count()

    # Save push-up count to database
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if user_profile:
        user_profile.pushups = count
    else:
        user_profile = UserProfile(user_id=current_user.id, pushups=count)
        db.session.add(user_profile)

    db.session.commit()
    db.session.flush()  # Force immediate database sync
    return jsonify({"message": "Push-ups saved!", "count": count})


@main.route("/pushup_test")
@login_required
def pushup_test():
    return render_template("pushup_test.html")

# @main.route('/register_admin', methods=['GET', 'POST'])
# def register_admin():
#     if current_user.is_authenticated and current_user.is_admin:
#         form = RegistrationForm()
#         if form.validate_on_submit():
#             user = User(email=form.email.data, is_admin=True)  # Set is_admin=True
#             user.set_password(form.password.data)
#             db.session.add(user)
#             db.session.commit()
#             flash('Admin registration successful!', 'success')
#             return redirect(url_for('main.input'))
#         return render_template('register_admin.html', form=form)
#     else:
#         flash('You do not have permission to access this page.', 'danger')
#         return redirect(url_for('main.input'))


def add_exercise_if_not_exists(exercise_data):
    exercise_name = exercise_data['Exercise Name']
    print(exercise_data)
    # Check if the exercise already exists
    existing_exercise = Exercise.query.filter_by(name=exercise_name).first()

    if existing_exercise:
        return existing_exercise  # Return the existing exercise if it exists

    # Add the exercise to the database if it doesn't exist
    new_exercise = Exercise(
        name=exercise_data['Exercise Name'],
    )

    db.session.add(new_exercise)
    db.session.commit()

    return new_exercise


@main.route('/fitness_test', methods=['GET', 'POST'])
@login_required
def fitness_test():
    form = FitnessTestForm()

    if form.validate_on_submit():
        # Get new scores
        pushups = form.pushups.data
        squats = form.squats.data
        user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()


        # Determine new fitness level
        new_fitness_level = classify_fitness_level(user_profile.gender, user_profile.age, pushups, squats)
        fitness_rank = {'poor': 1, 'below_avg': 2, 'average': 3, 'above_avg': 4, 'excellent': 5}

        if fitness_rank[new_fitness_level] > fitness_rank.get(user_profile.fitness_level):
            user_profile.fitness_level = new_fitness_level
            user_profile.pushups = pushups
            user_profile.squats = squats
            print(user_profile.fitness_level)
            flash(f"Great job! Your fitness level is now **{new_fitness_level}**. You'll get a new workout plan!",
                  "success")

        db.session.commit()
        return redirect(url_for('main.schedule'))

    return render_template('fitness_test.html', form=form)

@main.route('/customize_workout', methods=['GET', 'POST'])
@login_required
def customize_workout():
    user_id = current_user.id
    workout_pref = WorkoutPreferences.query.filter_by(user_id=user_id).first()

    muscle_groups = ['Chest', 'Triceps', 'Back', 'Biceps', 'Legs', 'Shoulders', 'Abs']

    if request.method == 'POST':
        # Store multiple selections as comma-separated values
        workout_pref_data = {
            "user_id": user_id,
            "monday": ",".join(request.form.getlist('monday')),
            "tuesday": ",".join(request.form.getlist('tuesday')),
            "wednesday": ",".join(request.form.getlist('wednesday')),
            "thursday": ",".join(request.form.getlist('thursday')),
            "friday": ",".join(request.form.getlist('friday')),
            "saturday": ",".join(request.form.getlist('saturday')),
            "sunday": ",".join(request.form.getlist('sunday'))
        }

        if workout_pref:
            # Update existing preferences
            for key, value in workout_pref_data.items():
                setattr(workout_pref, key, value)
        else:
            # Create new preferences
            workout_pref = WorkoutPreferences(**workout_pref_data)
            db.session.add(workout_pref)

        db.session.commit()
        flash('Workout preferences updated!', 'success')
        return redirect(url_for('main.schedule'))

    return render_template('customize_workout.html', workout_pref=workout_pref, muscle_groups=muscle_groups)

@main.route('/reset_db', methods=['GET'])
def reset_db():
    from app import db
    from flask_migrate import upgrade, downgrade
    import os
    try:
        print("Resetting DB with migrations...")
        # Drop and recreate the database using Alembic migration
        db.drop_all()
        db.session.commit()
        os.system("flask db upgrade")
        print("DB reset with migration done.")
        return 'Database reset with migration', 200
    except Exception as e:
        return f"Error resetting database: {str(e)}", 500
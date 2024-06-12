import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, overload

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Check that password and confirmation match
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            return apology("passwords do not match", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username does not exist
        if len(rows) == 1:
            return apology("username already exists", 400)
        elif len(rows) == 0:
            db.execute(
                "INSERT INTO users (username, hash, email) VALUES (?,?,?)", request.form.get(
                    "username"), generate_password_hash(password), request.form.get("email")
            )

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/create_workout", methods=["GET", "POST"])
@login_required
def create_workout():
    if request.method == "POST":
        # Check that Title and wourkout are populated
        if not request.form.get("title"):
            return apology("Please give your workout a name")
        if not request.form.get("exercise1"):
            return apology("Add at least one exercise")

        db.execute(
            "INSERT INTO workouts (userid, title) VALUES (?,?)", session["user_id"], request.form.get("title")
        )

        workout_id = db.execute(
            "SELECT id FROM workouts WHERE userid = ? AND title = ?", session["user_id"], request.form.get("title")
        )[0]['id']
        # Get workout data off UI
        rows = []
        rownum = 1

        # print(request.form)

        while True:
            exercise = request.form.get(f'exercise{rownum}')
            sets = request.form.get(f'sets{rownum}')
            reps = request.form.get(f'reps{rownum}')
            weight = request.form.get(f'weight{rownum}')

            # print(exercise)
            # print(sets)
            # print(reps)
            # print(weight)

            if not exercise or not sets or not reps or not weight:
                break

            rows.append({
                'exercise': exercise, 'sets': sets, 'reps': reps, 'weight': weight
            })
            rownum += 1

        # print(rows)

        # Workout data into db
        for row in rows:
            exercise = row['exercise']
            sets = row['sets']
            reps = row['reps']
            weight = row['weight']
            db.execute(
                "INSERT INTO workout_details (workoutid, exercisename, sets, reps, weight) VALUES (?,?,?,?,?)", workout_id, exercise, sets, reps, weight
            )
        # Redirect to Home page
        return redirect("/")
    else:
        return render_template("create_workout.html")

@app.route("/create_program", methods=["GET", "POST"])
@login_required
def create_program():
    if request.method == "POST":
        # Check that Title and wourkout are populated
        if not request.form.get("title"):
            return apology("Please give your program a name")
        if not request.form.get("week1"):
            return apology("Add at least one week of programming")

        # Create program skeleton
        db.execute(
            "INSERT INTO programs (userid, name) VALUES (?,?)", session["user_id"], request.form.get("title")
        )

        program_id = db.execute(
            "SELECT id FROM programs WHERE userid = ? AND name = ?", session["user_id"], request.form.get("title")
        )[0]['id']
        # Get program data off UI
        rows = []
        rownum = 1

        while True:
            week = request.form.get(f"week{rownum}")
            day = request.form.get(f"day{rownum}")
            workout_id = request.form.get(f"workout{rownum}")
            # print(week)
            # print(day)
            # print(workout_id)
            if not week or not day or not workout_id:
                break

            rows.append({
                'week': week, 'day': day, 'workout': workout_id
            })
            rownum += 1

        print(rows)
        # Get program data into db
        for row in rows:
            week = row['week']
            day = row['day']
            workout_id = row['workout']
            db.execute(
                "INSERT INTO program_details (programid, week, day, workoutid) VALUES (?,?,?,?)", program_id, week, day, workout_id
            )
        # Redirect to Home page
        return redirect("/")
    else:
        workouts = db.execute(
            "SELECT id, title FROM workouts ORDER BY title"
        )
        return render_template("create_program.html", workouts=workouts)

@app.route("/select_program", methods=["GET", "POST"])
@login_required
def select_program():
    if request.method == "POST":
        # Find selected program
        program_id = db.execute(
            "SELECT id FROM programs WHERE id = ?", request.form.get("choice")
        )[0]['id']
        db.execute(
            "UPDATE users SET active_program = ? WHERE id = ?", program_id, session["user_id"]
        )
        # Find first workout in selected program
        workout = db.execute(
            "SELECT workoutid FROM program_details WHERE programid = ? AND week = 1 AND day = 1", program_id
        )[0]['workoutid']
        session['workout'] = workout

        return redirect("/track")
    else:
        programs = db.execute(
            "SELECT id, name FROM programs"
        )
        return render_template("select_program.html", programs=programs)

@app.route("/track", methods=["GET", "POST"])
@login_required
def track_workout():
    if request.method == "POST":
        # Get current date/time
        current_date = datetime.date.today()

        # Initialize workout table
        workout_data = []

        # Set workout name/id
        workout_name = request.form.get('title')
        workout_id = session['workout']

        workout_data = db.execute(
            "SELECT * FROM workout_details WHERE workoutid = ?", workout_id
        )
        # print(workout_data)

        # Get workout data ready for tracking table
        rows = []
        key = 1
        for exercise in workout_data:
            new_weight = request.form.get(f'weight{key}')
            exercise['weight'] = new_weight
            new_reps = request.form.get(f'reps{key}')
            exercise['reps'] = new_reps
            exercisename = exercise['exercisename']
            sets = exercise['sets']
            reps = exercise['reps']
            weight = exercise['weight']
            # print(exercise)
            # print(sets)
            # print(reps)
            # print(weight)
            if not exercisename or not sets or not reps or not weight:
                break

            rows.append({
                'exercise': exercisename, 'sets': sets, 'reps': reps, 'weight': weight
            })
            key += 1

        # print(rows)
        # Workout data into db
        for row in rows:
            exercise = row['exercise']
            sets = row['sets']
            reps = row['reps']
            weight = row['weight']
            db.execute(
                "INSERT INTO track (userid, workoutid, exercisename, sets, reps, weight, date) VALUES (?,?,?,?,?,?,?)", session['user_id'], workout_id, exercise, sets, reps, weight, current_date
            )
            active_program = db.execute(
                "SELECT active_program FROM users WHERE id = ?", session["user_id"]
            )
            # if active_program:
            #     program_detail_id = db.execute(
            #         "SELECT id FROM program_details WHERE
            #     )
            #     db.execute(
            #         "INSERT INTO last_completed_workout (user_id, program_detail_id, date_completed) VALUES (?,?,?,?,?)", session["user_id"], exercise, sets, reps, weight
            #     )
        return redirect("/")
    else:
        if session.get('workout') is None:
            return redirect("/")
        else:
            workout = []
            workout = db.execute(
                "SELECT * FROM workout_details WHERE workoutid = ?", session['workout']
            )
            title = db.execute(
                "SELECT title FROM workouts WHERE id = ?", session['workout']
            )[0]['title']
            # Check if user has completed this workout before for overload purposes
            last = db.execute(
                "SELECT * FROM track WHERE workoutid = ? AND userid = ?", session['workout'], session['user_id']
            )
            if last:
                workout = overload(session['workout'])

            return render_template("/track.html", workout=workout, title=title)

@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    if request.method == "POST":

        # Get selected workout from table
        workout = request.form.get('choice')
        session['workout'] = workout

        return redirect("/track")
    else:
        workouts = db.execute(
            "SELECT id, title FROM workouts"
        )
        return render_template("/index.html", workouts=workouts)

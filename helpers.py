import csv
import datetime
import pytz
import requests
import urllib
import uuid

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def overload(workout):
    # Setup comparison workouts
    last = db.execute(
        "SELECT exercisename, reps, weight, date FROM track WHERE workout_id = ? ORDER BY date DESC LIMIT 1", workout
    )
    original = db.execute(
        "SELECT exercisename, reps, weight FROM workout_details WHERE workout_id = ?", workout
    )

    # initialize overloaded workout
    overloaded = []

    # overload calc
    for exercise in last:
        if exercise['reps'] < original[exercise]['reps'] + 2:
            overloaded[exercise]['reps'] = exercise['reps'] + 1
            overloaded[exercise]['weight'] = exercise['weight']
        elif exercise['reps'] >= original[exercise]['reps'] + 2:
            overloaded[exercise]['reps'] = exercise['reps']
            overloaded[exercise]['weight'] = exercise['weight'] + 5

    return overloaded



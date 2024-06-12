# PROGRESSIVE OVERLOAD

#### VIDEO DEMO: https://youtu.be/gkrNBA_UOFY
#### DESCRIPTION:

This project helps solve a problem I have personally had with strength training apps since I started tracking my workouts digitally in college more than 10 years ago. Any serious trainer I have talked to or read an article by has preached the benefits of "Progressive Overload" in order to maximise strength gains. But no app I have used yet has actually implemented this idea into its usage. Everything has been a mirror of what I did the previous lift and I was always stagnant in my progress. My app changes that.

## Templates
Let's start with the UI. I have used a number of HTML templates to try and create the cleanest user experience I can for my first full stack application. These templates include:
- apology
- create_program
- create_workout
- index
- layout
- login
- register
- select_program
- track

### apology.html
This one is lifted directly from the Finance project. I really liked the formatting of it, and it got all the information across that I needed it to. My compliments to the CS50 team for this!

### create_program
This page allows a user to create a lifting schedule for themselves. For this, I debated between creating a popup box that would ask the user for the number of weeks they want their program to run and the number of workouts per week they wanted to schedule. I decided against this because I have run a few programs that have differed slightly from week to week. Some 3 days, some 4 days. I decided to give my users that flexibility as well, so I created a script in this page to add rows to my form. This includes a `<select>` input that is a list of all workouts that have been created.

### create_workout
This page is very similar to the previous one, only for the individual workouts. I used a similar script to add rows to my workout table.

### index
My home page after login. This page is a list of all workouts that have been created by any user, and any can be selected to track a workout. If a user is already in a program, there is also a button that will continue them on their program.

### layout
The formatting on my page that will not change from page to page.

### login
A simple login page. Username, password, Login button. Easy peasy.

### register
A login page with additional fields for email and confirming a newly entered password. Also very simple.

### select_program
Built in a similar way to the `index.html` page, I debated making this one a `<select>` dropdown instead. Eventually I settled on this format to allow the user to see all of the available programs without having to make an extra click. It also seemed more natural to me than a nearly blank page with a single dropdown.

### track
Here is where the bulk of the user's time will likely be spent. This page has all the data populated for an individual workout, and allows a user to adjust their reps or weight lifted if necessary. This data will then be stored in a separate tracking table to allow for the overload calculation to occur.

## Database
This app uses a fairly simple database written in SQLite. It has 8 tables, which is more than I anticipated initially. Using Foreign Key combinations as Primary Keys was a good refresher for me, as it's been a while since I've worked on database structures. I did put a `Unique Index` on the username, which was an entirely new concept to me. I anticipated that having to be an id thing, but I was pleasantly surprised to find this little addition. In order to keep my Primary Keys, I had to create a `workout` table and a `workout_details` table (with the same idea for programs).

## helpers.py
This is another one that is based on the Finance project. I took what I could reuse from there and added my `overload()` function to it. The entire app is based around this idea:
```
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
```
This function will automatically take the latest time a user has completed a workout and will increase either their reps by 1, or the weight by 5 pounds. I've done this based on my own current home gym setup, which only allows me to move in 5 pound increments. This could easily be modified to allow for different overload ranges down the line.

## app.py
The place where everything else lives. All my routes are here, and handle all of the integration between my database and the frontend.

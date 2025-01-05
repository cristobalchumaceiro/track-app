import fitparse

from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_db, close_db, login_required, time_elapsed, distance_conv, pace_calc

app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Register the databse teardown
app.teardown_appcontext(close_db)


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    if user_id:
        return redirect("/activity_log")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log In User"""

    # Forget any user id
    session.pop("user_id", None)

    if request.method == "POST":

        # Create variables with values from input fields
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if any fields are missing values
        if not username or not password:
            flash("Username and/or password not entered")
            return redirect("/login")

        # Query database for id, username, and password
        db = get_db()
        row = db.execute(
            "SELECT id, username, password FROM users WHERE username = ?", (username,)
        ).fetchone()

        # Ensure username exists and password is correct
        if row is None or not check_password_hash(row["password"], password):
            flash("Invalid username and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = row["id"]

        # Redirect user to home page
        flash("Logged in successfully")
        return redirect("/activity_log")

    if request.method == "GET":
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log User Out"""

    # Forget any user id
    session.pop("user_id", None)

    # Redirect user to home page
    flash("Logged out successfully")
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register User"""
    if request.method == "POST":

        # Create variables with values from input fields
        username = request.form.get("username")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if any fields are missing values
        if not username or not firstname or not lastname or not password or not confirmation:
            flash("Username and/or password not entered")
            return redirect("/register")

        # Check if password matches confirmation
        if password != confirmation:
            flash("Passwords do not match")
            return redirect("/register")

        # Check if username already exists
        db = get_db()
        if db.execute(
            "SELECT username FROM users WHERE username = ?", (username,)
        ).fetchone():
            flash("Username already exists")
            return redirect("/register")

        # Generate hash for password and insert into users table
        hash = generate_password_hash(password, method='scrypt', salt_length=16)
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username, firstname, lastname, password) VALUES(?, ?, ?, ?)",
            (username, firstname, lastname, hash),
        )
        db.commit()

        flash("User created successfully")
        return redirect("/login")

    """Show Register Page"""
    if request.method == "GET":
        return render_template("register.html")


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Upload Activity"""
    if request.method == "POST":

        name = request.form.get("name")
        desc = request.form.get("description")

        # Retrieve uploaded .fit file from input field
        file = request.files.get("fitfile")
        if file:
            try:

                # Read file into object
                file_data = file.read()
                user_id = session["user_id"]
                if not user_id:
                    flash("User session expired. Please log in again.")
                    return redirect("/login")
                try:
                    fitfile = fitparse.FitFile(file_data)

                except Exception as e:
                    flash("An error occurred while reading the file. Please try again.")
                    return redirect("/upload")

                # Extract data from file
                fit_session = next(fitfile.get_messages("session"))
                date = fit_session.get_value("start_time")
                duration = time_elapsed(fit_session.get_value("total_elapsed_time"))
                if fit_session.get_value("total_distance") is not None:
                    distance = distance_conv(fit_session.get_value("total_distance"))
                    pace = pace_calc(fit_session.get_value("total_elapsed_time"), fit_session.get_value("total_distance"))
                else:
                    distance = None
                    pace = None
                calories = fit_session.get_value("total_calories")
                heartrate = fit_session.get_value("avg_heart_rate")

                fit_sport = next(fitfile.get_messages("sport"))
                sport = fit_sport.get_value("name")

                if not name:
                    name = sport

                # Insert file into database and get activity_id
                db = get_db()
                cursor = db.cursor()
                if not distance and pace:
                    cursor.execute(
                        "INSERT INTO activities (userId, fileData, sport, name, desc, date, duration, calories, heartrate) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (user_id, file_data, sport, name, desc, date, duration, calories, heartrate)
                    )
                    activity_id = cursor.lastrowid
                    db.commit()
                else:
                    cursor.execute(
                        "INSERT INTO activities (userId, fileData, sport, name, desc, date, duration, distance, pace, calories, heartrate) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (user_id, file_data, sport, name, desc, date, duration, distance, pace, calories, heartrate)
                    )
                    activity_id = cursor.lastrowid
                    db.commit()

                # Pass activity_id to activity page to display data
                flash("Activity uploaded sccuessfully")
                return redirect(f"/activity/{activity_id}")
            except Exception as e:
                print(e)
                flash("An error occurred while uploading the activity. Please try again.")
                return redirect("/upload")
        else:
            flash("No file uploaded.")
            return redirect("/upload")

    """Show Upload Page"""
    if request.method == "GET":
        return render_template("upload.html")


@app.route("/activity/<int:activity_id>")
@login_required
def activity(activity_id):
    """Show Activity Page"""
    user_id = session["user_id"]
    if not user_id:
        flash("User session expired. Please log in again.")
        return redirect("/login")

    db = get_db()
    activity = db.execute(
        "SELECT * FROM activities WHERE id = ?",
        (activity_id,)
    ).fetchone()

    if not activity:
        flash("Activity not found.")
        return redirect("/activity_log")

    # Format stored date
    date_object = datetime.strptime(activity['date'], "%Y-%m-%d %H:%M:%S")
    f_date = date_object.strftime("%H:%M on %A, %d %B %Y")

    # Check if activity exists
    if activity:
        file_data = activity[2]
        fitfile = fitparse.FitFile(file_data)

    # Extract location data from file
        location_data = []
        for fit_session in fitfile.get_messages("record"):
            lat = fit_session.get_value("position_lat")
            lng = fit_session.get_value("position_long")
            if lat and lng:
                location_data.append({
                    "lat": lat * (180 / 2**31),
                    "lng": lng * (180 / 2**31)
                })

        return render_template("activity.html", activity=activity, f_date=f_date, location_data=location_data)
    else:
        flash("Activity not found.")
        return redirect("/upload")


@app.route("/edit_activity/<int:activity_id>", methods=["GET", "POST"])
@login_required
def edit_activity(activity_id):
    """Edit Activity Page"""
    user_id = session["user_id"]
    if not user_id:
        flash("User session expired. Please log in again.")
        return redirect("/login")

    db = get_db()

    if request.method == "GET":

        # Query database for activity
        activity = db.execute(
            "SELECT * FROM activities WHERE id = ? AND userID = ?",
            (activity_id, user_id,)
        ).fetchone()

        # Format stored date
        date_object = datetime.strptime(activity['date'], "%Y-%m-%d %H:%M:%S")
        f_date = date_object.strftime("%H:%M on %A, %d %B %Y")

        if activity:
            file_data = activity[2]
            fitfile = fitparse.FitFile(file_data)

            # Extract location data from file
            location_data = []
            for fit_session in fitfile.get_messages("record"):
                lat = fit_session.get_value("position_lat")
                lng = fit_session.get_value("position_long")
                if lat and lng:
                    location_data.append({
                        "lat": lat * (180 / 2**31),
                        "lng": lng * (180 / 2**31)
                    })
            return render_template("edit_activity.html", activity=activity, f_date=f_date, location_data=location_data)
        else:
            flash("Activity not found or user not allowed to edit this activity.")
            return redirect("/upload")

    if request.method == "POST":

        # Check if the delete button was clicked
        if "delete" in request.form:
            cursor = db.cursor()
            cursor.execute(
                "DELETE FROM activities WHERE id = ? AND userID = ?",
                (activity_id, user_id)
            )
            db.commit()
            flash("Activity deleted successfully.")
            return redirect("/activity_log")

        # Update activity name and description
        name = request.form.get("name")
        desc = request.form.get("description")

        cursor = db.cursor()
        activity = cursor.execute(
            "UPDATE activities SET name = ?, desc = ? WHERE id = ? AND userID = ?",
            (name, desc, activity_id, user_id,)
        )
        db.commit()

        flash("Activity edited successfully.")
        return redirect(f"/activity/{activity_id}")


@app.route("/activity_log", methods=["GET"])
@login_required
def profile():
    """Show Activity Log"""
    user_id = session["user_id"]
    db = get_db()

    # Query database for user's first and last name
    profile = db.execute(
        "SELECT firstname, lastname FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    # Query database for all activities for the user
    activity_data = db.execute(
        "SELECT id, sport, name, date, duration, distance FROM activities WHERE userId = ? ORDER BY date DESC",
        (user_id,)
    ).fetchall()

    # Format dates
    f_date = []

    for row in activity_data:
        date_object = datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")
        f_date.append(date_object.strftime("%a, %d/%m/%Y"))

    return render_template("activity_log.html", profile=profile, activity_data=activity_data, f_date=f_date)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error="404 Page Not Found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error="500 Internal Server Error"), 500
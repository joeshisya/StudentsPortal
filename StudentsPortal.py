import binascii
import collections
import gc
import logging
import math
import os
from functools import wraps

from flask import Flask, render_template, redirect, url_for, request, flash, session, send_file
from flask_mail import Mail

import MyMail
import gmailSettings
from dbConnect import DbConnect

app = Flask(__name__)
app.secret_key = "THOU_SHALT_NOT_KNOW_THINE_SECRET_KEY"
app.debug = True
app.config.update(
    TEMPLATES_AUTO_RELOAD=True
)

app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER=gmailSettings.mail_server,
    MAIL_PORT=gmailSettings.mail_port,
    MAIL_USE_SSL=gmailSettings.mail_use_ssl,
    MAIL_USERNAME=gmailSettings.mail_username,
    MAIL_PASSWORD=gmailSettings.mail_password
)
mail = Mail(app)

log = os.path.join(os.path.dirname(__file__), 'logs/error_log')
handler = logging.FileHandler(log)
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)


# Used to ensure that a user is logged in before accessing certain pages
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("YOU HAVE TO BE LOGGED IN!")
            return redirect(url_for('login'))

    return wrap


# Used to limit certain pages to lectures only
def lecturer_only(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_type' in session and session['user_type'] == "lecturer":
            return f(*args, **kwargs)
        else:
            flash("YOU NEED TO BE A LECTURER TO VIEW THAT PAGE!")
            return redirect(url_for('home'))

    return wrap


# Used to limit certain pages to administrators only
def admin_only(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_type' in session and session['user_type'] == "admin":
            return f(*args, **kwargs)
        else:
            flash("YOU NEED TO BE AN ADMIN TO VIEW THAT PAGE!")
            return redirect(url_for('home'))

    return wrap


def logged_in(reg_no):
    session['logged_in'] = True
    session['registration_number'] = reg_no
    session['admin'] = False
    flash("YOU HAVE SUCCESSFULLY LOGGED IN!!")


# Home page
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/student/login/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        reg_no = request.form['reg_no']
        password = request.form['password']

        if not reg_no:
            return render_template("login.html", username_error="USERNAME CANNOT BE BLANK")

        if not password:
            return render_template("login.html", password_error="PASSWORD CANNOT BE BLANK")

        try:
            connection = DbConnect("students")
            if connection.confirm_account(reg_no, password):
                logged_in(reg_no)
                return redirect(url_for("dashboard"))

            else:
                return render_template("login.html", error="INVALID CREDENTIALS. TRY AGAIN!")

        except Exception as e:
            return render_template("login.html", error=e)

    return render_template("login.html")


@app.route('/student/request_password_reset', methods=["GET", "POST"])
def request_password_reset():
    if request.method == "POST":
        attempted_registration_number = request.form.get('registration_number')

        connection = DbConnect("students")
        if connection.user_exists(attempted_registration_number):
            reset_code = binascii.hexlify(os.urandom(24)).decode('ascii')

            message = """ You are receiving this email because someone has requested for password reset for your 
            account. Click on the link below to reset your password. If you cannot click the link, copy and  paste it 
            into your browser \n\n 
            
            http://127.0.0.1:5000/student/reset_password/{0} \n\n
            
            If you did not submit a password reset request, please ignore this email. \n\n\n

            """.format(reset_code)

            if MyMail.send_mail(mail, message):
                connection = DbConnect("students")
                connection.add_password_reset_code(reset_code, attempted_registration_number)
                flash('Please Check Your Email')
                return redirect(url_for('home'))

        else:
            error = "User does not exist!"
            return render_template("request_password_request.html", error=error)

    return render_template("request_password_request.html")


@app.route('/student/reset_password/')
@app.route('/student/reset_password/<reset_code>', methods=["GET", "POST"])
def reset_password(reset_code=None):
    if request.method == "POST":
        if 'user_to_change' in session:
            password = request.form.get('password')
            password_repeat = request.form.get('password_repeat')

            if password == password_repeat:
                connection = DbConnect("students")
                connection.change_password(session['user_to_change'], password)

                flash("LOGIN WITH NEW PASSWORD")
                return redirect(url_for("login"))

            else:
                error = "Both passwords need to be the same. Please try again"
                return render_template("request_password_request.html", error=error)

        else:
            return redirect(url_for("request_password_reset"))

    else:
        if not reset_code:
            return redirect(url_for("request_password_reset"))

        connection = DbConnect("students")
        result = connection.is_valid_password_reset_link(reset_code)

        if result:
            session['user_to_change'] = result['registration_number']
            return render_template("reset_password.html")

        else:
            return redirect(url_for("request_password_reset"))


@app.route('/student/dashboard/')
@login_required
def dashboard():
    if 'student_details' not in session:
        connection = DbConnect("students")
        session['student_details'] = connection.get_student_details(session['registration_number'])

    return render_template("dashboard/dashboard.html")


@app.route('/student/dashboard/inbox')
@login_required
def inbox():
    return render_template("production/in_progress.html")


@app.route('/student/dashboard/settings')
@login_required
def settings():
    return render_template("dashboard/settings.html")


@app.route('/student/logout/')
@login_required
def logout():
    session.clear()
    flash("YOU HAVE BEEN LOGGED OUT!!")
    gc.collect()
    return redirect(url_for("home"))


@app.route('/student/dashboard/student_details')
@login_required
def student_details():
    try:
        details = session['student_details']

        return render_template("dashboard/student_details.html", details=details)

    except Exception as e:
        flash(e)
        return render_template("dashboard/student_details.html")


@app.route('/student/dashboard/timetable')
@login_required
def timetable():
    connection = DbConnect("students")
    result = connection.get_timetable(session['student_details'])

    m = []
    t = []
    w = []
    th = []
    f = []
    s = []

    for r in result:
        if r['day_of_week'] == "Monday":
            m.append(r)
        elif r['day_of_week'] == "Tuesday":
            t.append(r)
        elif r['day_of_week'] == "Wednesday":
            w.append(r)
        elif r['day_of_week'] == "Thursday":
            th.append(r)
        elif r['day_of_week'] == "Friday":
            f.append(r)
        elif r['day_of_week'] == "Saturday":
            s.append(r)

    return render_template("dashboard/timetable.html", m=m, t=t, w=w, th=th, f=f, s=s)


@app.route('/student/dashboard/accommodation', methods=["GET", "POST"])
@login_required
def accommodation():
    if request.method == "POST":
        preferred_hostel = request.form.get('preferred_hostel')

        if preferred_hostel == "ANY CAN DO":
            preferred_hostel = session['hostels'][0]['hostel_name']

        connection = DbConnect("university")
        connection.occupied_hostel(preferred_hostel)

        connection = DbConnect("student")
        connection.assign_hostel(preferred_hostel, session['registration_number'])

        session['student_details']['hostel'] = preferred_hostel
        alert = "YOU ARE NOW A MEMBER OF {0}. TOO LAZY TO ADD ROOM NUMBER NOW, EXPECT IT LATER".format(preferred_hostel)
        flash(alert)

        return redirect(url_for('student_details'))

    else:
        if not session['student_details']['hostel']:
            if 'hostels' not in session:
                gender = session['student_details']['gender']
                connection = DbConnect("university")
                hostels = connection.available_hostels(gender)
                session['hostels'] = hostels

            else:
                hostels = session['hostels']

            return render_template("dashboard/accommodation.html", hostels=hostels)

        else:
            cant_book = True
            return render_template("dashboard/accommodation.html", cant_book=cant_book)


@app.route('/student/dashboard/cats_and_exams')
@login_required
def cats_and_exams():
    db = DbConnect('students')
    exams = db.get_exams(session['student_details'])

    result = collections.defaultdict(list)

    for exam in exams:
        result[exam['unit_code']].append(exam)

    exam_list = result.values()

    for exam in exams:
        if exam['start_time'] == exam['end_time']:
            exam['start_time'] = exam['end_time'] = "N/A"

    return render_template("dashboard/cats_and_exams.html", exam_list=exam_list)


@app.route('/student/dashboard/results')
@login_required
def results():
    db = DbConnect("students")
    scores = db.get_scores(session['student_details']['registration_number'])

    one = []
    two = []
    three = []
    four = []
    five = []
    six = []
    all_scores = [one, two, three, four, five, six]

    for score in scores:
        for key in score:
            if not score[key]:
                score[key] = "N/A"

    for score in scores:
        if score['score_year'] == 1:
            one.append(score)
        if score['score_year'] == 2:
            two.append(score)
        if score['score_year'] == 3:
            three.append(score)
        if score['score_year'] == 4:
            four.append(score)
        if score['score_year'] == 5:
            five.append(score)
        if score['score_year'] == 6:
            six.append(score)

    return render_template("dashboard/results.html", scores=all_scores)


@app.route('/student/dashboard/notes')
@login_required
def notes():
    connection = DbConnect("students")
    files = connection.get_documents("Computer Science", session['student_details']['current_year'],
                                     session['student_details']['current_semester'])

    return render_template("dashboard/notes.html", files=files)


@app.route('/student/dashboard/attendance')
@login_required
def attendance():
    return render_template("production/in_progress.html")


@app.route('/student/dashboard/fees')
@login_required
def fees():
    db = DbConnect("students")
    history = db.get_payment_history(session['student_details'])
    statement = db.get_fee_statement(session['student_details'])
    paid = history[-1]['transaction_amount']
    over_p =  math.fabs(history[-2]['balance_after'])

    return render_template("dashboard/fees.html", payment_history=history, fee=statement['total_amount'], over_p=over_p,
                           paid=paid)


@app.route('/student/dashboard/notes/<path:file>')
@login_required
def download_file(file):
    file = os.path.join(os.path.dirname(__file__), file)
    return send_file(file)


@app.route('/admin/add_student/', methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        # Ensure that all necessary fields were filled
        # Returns an error message if not
        if not (request.form.get('registration_number') and request.form.get('first_name') and
                request.form.get('last_name') and request.form.get('mode_of_admission') and
                request.form.get('level') and request.form.get('course') and request.form.get('email') and
                request.form.get('gender') and request.form.get('dob') and request.form.get('disabled') and
                request.form.get('faculty') and request.form.get('year') and request.form.get('semester')):
            return render_template("admin/add_student.html", error="PLEASE FILL IN ALL MANDATORY FIELDS!")

        try:
            connection = DbConnect("students")
            connection.add_account(request.form)

            flash("New Student Successfully Added")
            return render_template("admin/add_student.html")

        except Exception as e:
            e = str(e)
            return render_template("admin/add_student.html", error=e)

    return render_template("admin/add_student.html")


# Handles bad request errors
@app.errorhandler(400)
def bad_request(e):
    return render_template("errors/400.html", error=e)


# Handles page not found errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html", error=e)


# Handles internal server errors
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("errors/500.html", error=e)


# Run
if __name__ == '__main__':
    app.run()

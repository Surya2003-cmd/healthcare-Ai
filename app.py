import os
from datetime import date

from flask import Flask, render_template, request, redirect, session, jsonify, send_file
from models.diabetes_model import predict_diabetes
from models.heart_model import predict_heart

import mysql.connector
from chatbot.openai_chatbot import ask_openai
from pdf_reports.report_generator import generate_report

# ==========================================================
# MYSQL DATABASE CONNECTION
# ==========================================================

db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", "Aishu@2003"),
    database=os.getenv("MYSQL_DATABASE", "healthcare")
)

cursor = db.cursor()

# ==========================================================
# FLASK CONFIGURATION
# ==========================================================

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "healthcare_ai_secret")

# ==========================================================
# HOME PAGE
# ==========================================================

@app.route('/')
def home():
    return render_template("auth/login.html")

# ==========================================================
# USER REGISTRATION
# ==========================================================

@app.route('/register')
def register():
    return render_template("auth/register.html")


@app.route('/register_user', methods=['POST'])
def register_user():

    try:

        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing = cursor.fetchone()

        if existing:
            return "Email already registered."

        cursor.execute(
            """
            INSERT INTO users
            (full_name,email,password_hash)
            VALUES(%s,%s,%s)
            """,
            (full_name, email, password)
        )

        db.commit()

        return redirect('/')

    except Exception as e:

        return f"Registration Error : {e}"

# ==========================================================
# USER LOGIN
# ==========================================================

@app.route('/login', methods=['POST'])
def login():

    try:

        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=%s
            AND password_hash=%s
            """,
            (email, password)
        )

        user = cursor.fetchone()

        if user:

            session['user_id'] = user[0]
            session['user_name'] = user[1]

            return redirect('/user')

        return "Invalid Email or Password"

    except Exception as e:

        return f"Login Error : {e}"

# ==========================================================
# LOGOUT
# ==========================================================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# ==========================================================
# USER DASHBOARD
# ==========================================================

@app.route('/user')
def user_dashboard():

    if 'user_id' not in session:
        return redirect('/')

    return render_template(
        "user/dashboard.html",
        username=session['user_name']
    )

# ==========================================================
# DOCTOR DASHBOARD
# ==========================================================

@app.route('/doctor')
def doctor_dashboard():

    return render_template(
        "doctor/dashboard.html"
    )

# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@app.route('/admin')
def admin_dashboard():

    return render_template(
        "admin/dashboard.html"
    )
# ==========================================================
# DISEASE PREDICTION PAGE
# ==========================================================

@app.route('/predict')
def predict_page():

    if 'user_id' not in session:
        return redirect('/')

    return render_template("user/predict.html")


# ==========================================================
# DIABETES PREDICTION
# ==========================================================

@app.route('/predict_diabetes', methods=['POST'])
def diabetes():

    try:

        age = float(request.form['age'])

        values = [

            float(request.form['pregnancies']),
            float(request.form['glucose']),
            float(request.form['bloodpressure']),
            float(request.form['skinthickness']),
            float(request.form['insulin']),
            float(request.form['bmi']),
            float(request.form['dpf']),
            age

        ]

        prediction = predict_diabetes(values)

        cursor.execute(
            "UPDATE users SET age=%s WHERE user_id=%s",
            (int(age), session['user_id'])
        )

        cursor.execute("""

        INSERT INTO predictions

        (user_id,disease,probability,result)

        VALUES(%s,%s,%s,%s)

        """,(session['user_id'],

             "Diabetes",

             prediction['probability'],

             prediction['result']))

        db.commit()

        return render_template(

            "user/result.html",

            disease="Diabetes",

            result=prediction

        )

    except Exception as e:

        return f"Prediction Error : {e}"


# ==========================================================
# HEART DISEASE PREDICTION
# ==========================================================

@app.route('/predict_heart', methods=['POST'])
def heart():

    try:

        age = float(request.form['age'])

        values=[

            age,
            float(request.form['sex']),
            float(request.form['cp']),
            float(request.form['trestbps']),
            float(request.form['chol']),
            float(request.form['fbs']),
            float(request.form['restecg']),
            float(request.form['thalach']),
            float(request.form['exang']),
            float(request.form['oldpeak']),
            float(request.form['slope']),
            float(request.form['ca']),
            float(request.form['thal'])

        ]

        prediction=predict_heart(values)

        cursor.execute(
            "UPDATE users SET age=%s WHERE user_id=%s",
            (int(age), session['user_id'])
        )

        cursor.execute("""

        INSERT INTO predictions

        (user_id,disease,probability,result)

        VALUES(%s,%s,%s,%s)

        """,(session['user_id'],

             "Heart Disease",

             prediction['probability'],

             prediction['result']))

        db.commit()

        return render_template(

            "user/result.html",

            disease="Heart Disease",

            result=prediction

        )

    except Exception as e:

        return f"Prediction Error : {e}"


# ==========================================================
# AI CHATBOT
# ==========================================================

@app.route('/chatbot')
def chatbot():

    if 'user_id' not in session:
        return redirect('/')

    return render_template("user/chatbot.html")


@app.route('/ask_chatbot', methods=['POST'])
def ask_chatbot():

    try:

        question=request.form['question']

        response=ask_openai(question)

        if 'user_id' in session:
            cursor.execute("""

            INSERT INTO chatbot_history

            (user_id,question,response)

            VALUES(%s,%s,%s)

            """,(session['user_id'], question, response))

            db.commit()

        return render_template(

            "user/chatbot.html",

            question=question,

            response=response

        )

    except Exception as e:

        return render_template(

            "user/chatbot.html",

            response=f"Chatbot Error : {e}"

        )


@app.route('/ai_suggestion', methods=['POST'])
def ai_suggestion():

    if 'user_id' not in session:
        return jsonify({
            "success": False,
            "suggestion": "Please login to use real-time AI suggestions."
        }), 401

    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    context = (data.get("context") or "real-time healthcare suggestion").strip()

    if len(question) < 8:
        return jsonify({
            "success": True,
            "suggestion": "Type a little more detail to get an AI suggestion."
        })

    try:
        suggestion = ask_openai(question, context=context)

        return jsonify({
            "success": True,
            "suggestion": suggestion
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "suggestion": f"AI Suggestion Error : {e}"
        }), 500


# ==========================================================
# DIET RECOMMENDATION
# ==========================================================

@app.route('/diet', methods=['GET','POST'])
def diet():

    recommendation=None

    if request.method=="POST":

        disease=request.form['disease']

        diet_data={

            "Diabetes":
            """
✔ Brown Rice

✔ Oats

✔ Green Vegetables

✔ Sugar Free Diet

✔ Drink 3 Litres Water
            """,

            "Heart Disease":
            """
✔ Fruits

✔ Fish

✔ Olive Oil

✔ Oats

✔ Low Salt Diet
            """,

            "Healthy":
            """
✔ Fruits

✔ Vegetables

✔ Protein

✔ Milk

✔ Plenty of Water
            """

        }

        recommendation=diet_data.get(disease)

    return render_template(

        "user/diet.html",

        recommendation=recommendation

    )


# ==========================================================
# PHYSIOTHERAPY
# ==========================================================

@app.route('/physiotherapy', methods=['GET','POST'])
def physiotherapy():

    recommendation=None

    if request.method=="POST":

        condition=request.form['condition']

        exercise={

            "Back Pain":
            """
✔ Child Pose

✔ Cat Cow Stretch

✔ Walking
            """,

            "Neck Pain":
            """
✔ Neck Stretch

✔ Chin Tuck

✔ Shoulder Roll
            """,

            "Knee Pain":
            """
✔ Quad Stretch

✔ Straight Leg Raise

✔ Cycling
            """,

            "Shoulder Pain":
            """
✔ Pendulum Exercise

✔ Arm Circle

✔ Shoulder Stretch
            """,

            "Healthy":
            """
✔ Yoga

✔ Walking

✔ Meditation
            """

        }

        recommendation=exercise.get(condition)

    return render_template(

        "user/physiotherapy.html",

        recommendation=recommendation

    )


# ==========================================================
# APPOINTMENT
# ==========================================================

def get_available_doctors():

    cursor.execute("""

    SELECT doctor_id, doctor_name, specialization

    FROM doctors

    ORDER BY doctor_name

    """)

    doctors = cursor.fetchall()

    if doctors:
        return doctors

    default_doctors = [
        ("Dr. Rajesh Kumar", "Cardiologist", "rajesh.cardiology@example.com"),
        ("Dr. Priya Sharma", "Diabetologist", "priya.diabetes@example.com"),
        ("Dr. Anil Reddy", "Orthopedic", "anil.ortho@example.com"),
        ("Dr. Sneha Patel", "Physiotherapist", "sneha.physio@example.com"),
    ]

    for doctor_name, specialization, email in default_doctors:
        cursor.execute("""

        INSERT INTO doctors

        (doctor_name,specialization,email,password_hash)

        VALUES(%s,%s,%s,%s)

        """,(doctor_name, specialization, email, "doctor123"))

    db.commit()

    cursor.execute("""

    SELECT doctor_id, doctor_name, specialization

    FROM doctors

    ORDER BY doctor_name

    """)

    return cursor.fetchall()


@app.route('/appointment')
def appointment():

    if 'user_id' not in session:
        return redirect('/')

    doctors = get_available_doctors()

    return render_template(

        "user/appointment.html",

        doctors=doctors,

        min_date=date.today().isoformat()

    )


@app.route('/book_appointment', methods=['POST'])
def book_appointment():

    if 'user_id' not in session:
        return redirect('/')

    doctors = get_available_doctors()

    try:

        doctor=request.form.get('doctor')

        appointment_date=request.form.get('date')

        appointment_time=request.form.get('time')

        symptoms=request.form.get('symptoms')

        if not doctor or not appointment_date:
            return render_template(
                "user/appointment.html",
                doctors=doctors,
                min_date=date.today().isoformat(),
                error="Please select a doctor and appointment date."
            )

        cursor.execute(
            "SELECT doctor_id FROM doctors WHERE doctor_id=%s",
            (doctor,)
        )

        selected_doctor = cursor.fetchone()

        if not selected_doctor:
            return render_template(
                "user/appointment.html",
                doctors=doctors,
                min_date=date.today().isoformat(),
                error="Selected doctor is not available."
            )

        cursor.execute("""

        SELECT appointment_id FROM appointments

        WHERE user_id=%s

        AND doctor_id=%s

        AND appointment_date=%s

        AND status IN ('Pending','Approved')

        """,(session['user_id'], doctor, appointment_date))

        existing_appointment = cursor.fetchone()

        if existing_appointment:
            return render_template(
                "user/appointment.html",
                doctors=doctors,
                min_date=date.today().isoformat(),
                error="You already have an active appointment with this doctor on the selected date."
            )

        cursor.execute("""

        INSERT INTO appointments

        (user_id,doctor_id,appointment_date,status)

        VALUES(%s,%s,%s,%s)

        """,(session['user_id'],

             doctor,

             appointment_date,

             "Pending"))

        db.commit()

        confirmation = (
            "Appointment booked successfully. "
            f"Preferred time: {appointment_time or 'Not specified'}. "
            f"Symptoms noted: {symptoms or 'Not provided'}."
        )

        return render_template(
            "user/appointment.html",
            doctors=doctors,
            min_date=date.today().isoformat(),
            message=confirmation
        )

    except Exception as e:

        db.rollback()

        return render_template(
            "user/appointment.html",
            doctors=doctors,
            min_date=date.today().isoformat(),
            error=f"Appointment Booking Error : {e}"
        )


# ==========================================================
# PDF REPORT PAGE
# ==========================================================

@app.route('/report')
def report():

    if 'user_id' not in session:
        return redirect('/')

    cursor.execute(
        "SELECT age FROM users WHERE user_id=%s",
        (session['user_id'],)
    )
    user = cursor.fetchone()
    age = user[0] if user and user[0] is not None else None

    cursor.execute("""
        SELECT
            prediction_id,
            disease,
            probability,
            result,
            created_at
        FROM predictions
        WHERE user_id=%s
        ORDER BY created_at DESC
        LIMIT 1
    """,(session['user_id'],))

    latest_prediction = cursor.fetchone()
    result = None
    created_at = None

    if latest_prediction:
        result = {
            "prediction_id": latest_prediction[0],
            "disease": latest_prediction[1],
            "probability": float(latest_prediction[2] or 0),
            "result": latest_prediction[3],
        }
        created_at = latest_prediction[4]

    return render_template(

        "user/report.html",
        username=session.get('user_name', 'Patient'),
        age=age,
        disease=result["disease"] if result else None,
        result=result,
        created_at=created_at

    )


@app.route('/download_report')
def download_report():

    if 'user_id' not in session:
        return redirect('/')

    cursor.execute(
        "SELECT age FROM users WHERE user_id=%s",
        (session['user_id'],)
    )
    user = cursor.fetchone()
    age = user[0] if user and user[0] is not None else None

    cursor.execute("""
        SELECT
            prediction_id,
            disease,
            probability,
            result,
            created_at
        FROM predictions
        WHERE user_id=%s
        ORDER BY created_at DESC
        LIMIT 1
    """,(session['user_id'],))

    latest_prediction = cursor.fetchone()

    report_data = {
        "patient_name": session.get('user_name', 'Patient'),
        "age": age,
        "prediction": None,
    }

    if latest_prediction:
        report_data["prediction"] = {
            "prediction_id": latest_prediction[0],
            "disease": latest_prediction[1],
            "probability": float(latest_prediction[2] or 0),
            "result": latest_prediction[3],
            "created_at": latest_prediction[4],
        }

    pdf_buffer = generate_report(report_data)
    filename = f"healthcare_report_user_{session['user_id']}.pdf"

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )
# ==========================================================
# DOCTOR REGISTRATION
# ==========================================================

@app.route('/doctor_register')
def doctor_register():
    return render_template('auth/doctor_register.html')


@app.route('/doctor_register_submit', methods=['POST'])
def doctor_register_submit():

    try:

        doctor_name = request.form['doctor_name']
        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            "SELECT * FROM doctors WHERE email=%s",
            (email,)
        )

        existing = cursor.fetchone()

        if existing:
            return "Doctor already registered."

        cursor.execute("""
            INSERT INTO doctors
            (doctor_name,email,password_hash)
            VALUES(%s,%s,%s)
        """,(doctor_name,email,password))

        db.commit()

        return redirect('/doctor_login')

    except Exception as e:

        return f"Registration Error : {e}"


# ==========================================================
# DOCTOR LOGIN
# ==========================================================

@app.route('/doctor_login')
def doctor_login():
    return render_template('auth/doctor_login.html')


@app.route('/doctor_login_submit', methods=['POST'])
def doctor_login_submit():

    try:

        email=request.form['email']
        password=request.form['password']

        cursor.execute("""
            SELECT *
            FROM doctors
            WHERE email=%s
            AND password_hash=%s
        """,(email,password))

        doctor=cursor.fetchone()

        if doctor:

            session['doctor_id']=doctor[0]
            session['doctor_name']=doctor[1]

            return redirect('/doctor')

        return "Invalid Doctor Credentials"

    except Exception as e:

        return str(e)


# ==========================================================
# ADMIN LOGIN
# ==========================================================

@app.route('/admin_login')
def admin_login():
    return render_template('auth/admin_login.html')


@app.route('/admin_login_submit', methods=['POST'])
def admin_login_submit():

    username=request.form['username']
    password=request.form['password']

    cursor.execute("""
        SELECT *
        FROM admins
        WHERE username=%s
        AND password_hash=%s
    """,(username,password))

    admin=cursor.fetchone()

    if admin:

        session['admin_id']=admin[0]

        return redirect('/admin')

    return "Invalid Admin Credentials"


# ==========================================================
# ADMIN MODULE
# ==========================================================

@app.route('/manage_users')
def manage_users():

    cursor.execute("""
        SELECT user_id,
               full_name,
               email
        FROM users
    """)

    users=cursor.fetchall()

    return render_template(
        "admin/manage_users.html",
        users=users
    )


@app.route('/manage_doctors')
def manage_doctors():

    cursor.execute("""
        SELECT doctor_id,
               doctor_name,
               email
        FROM doctors
    """)

    doctors=cursor.fetchall()

    return render_template(
        "admin/manage_doctors.html",
        doctors=doctors
    )


@app.route('/view_reports')
def view_reports():

    cursor.execute("""
        SELECT
        prediction_id,
        user_id,
        disease,
        probability,
        result,
        created_at
        FROM predictions
        ORDER BY created_at DESC
    """)

    reports=cursor.fetchall()

    return render_template(
        "admin/view_reports.html",
        reports=reports
    )


# ==========================================================
# DOCTOR MODULE
# ==========================================================

@app.route('/view_patients')
def view_patients():

    cursor.execute("""
        SELECT
        user_id,
        full_name,
        email
        FROM users
    """)

    patients=cursor.fetchall()

    return render_template(
        "doctor/view_patients.html",
        patients=patients
    )


@app.route('/add_recommendation')
def add_recommendation():

    return render_template(
        "doctor/add_recommendation.html"
    )


@app.route('/save_recommendation', methods=['POST'])
def save_recommendation():

    patient = request.form['patient']
    disease = request.form['disease']
    medicine = request.form['medicine']
    diet = request.form['diet']
    physiotherapy = request.form['physiotherapy']
    recommendation = request.form['recommendation']

    cursor.execute("""
        INSERT INTO recommendations
        (patient_name, disease, medicine, diet, physiotherapy, recommendation)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        patient,
        disease,
        medicine,
        diet,
        physiotherapy,
        recommendation
    ))

    db.commit()

    return redirect('/doctor_reports')


@app.route('/doctor_reports')
def doctor_reports():

    cursor.execute("""
        SELECT
            recommendation_id,
            patient_name,
            disease,
            medicine,
            diet,
            physiotherapy,
            recommendation,
            created_at
        FROM recommendations
        ORDER BY created_at DESC
    """)

    reports = cursor.fetchall()

    return render_template(
        "doctor/reports.html",
        reports=reports
    )


# ==========================================================
# DATABASE TEST
# ==========================================================

@app.route('/testdb')
def testdb():

    try:

        cursor.execute("SELECT DATABASE();")

        database=cursor.fetchone()

        return f"Connected Successfully : {database[0]}"

    except Exception as e:

        return str(e)


# ==========================================================
# ERROR HANDLER
# ==========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ),404

# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__=="__main__":

    app.run(
        debug=True
    )

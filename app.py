import os
import random
from datetime import datetime, timezone
import traceback

from services.volunteer_stats_service import get_dashboard_statistics
from services.volunteer_schedule_service import get_volunteer_schedule
from services.volunteer_hours_service import get_volunteer_hours

# Flask core imports
from flask import Flask, render_template, session, redirect, request, url_for, jsonify
from flask_migrate import Migrate

# Flask-Babel: handles multi-language support (English + Simplified Chinese)
from flask_babel import Babel, gettext as _

# Flask-Login: manages user session after login
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

# Flask-Mail: sends OTP verification emails to users
from flask_mail import Mail, Message

# Import database instance and User model from models.py
from models import *

app = Flask(__name__)

# Secret key used to sign session cookies — loaded from environment variable in production
app.secret_key = os.environ.get("SECRET_KEY", "fallback_only_for_dev")

# ── Flask-Babel Configuration (Multi-language support) ──────────────────────
# Added to support English and Simplified Chinese translations across all pages
app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"

# ── SQLAlchemy Configuration (Database) ─────────────────────────────────────
# Uses SQLite locally — wmaa.db file is created automatically on first run
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wmaa.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ── Flask-Mail Configuration (Email / OTP) ───────────────────────────────────
# Gmail SMTP is used to send OTP verification emails during signup
# Credentials are loaded from environment variables in production for security
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "harpreetvallah2@gmail.com")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "owoz huca itgc zvqj")
app.config["MAIL_DEFAULT_SENDER"] = ("WMAA Charity", "harpreetvallah2@gmail.com")

# Supported language codes — used in set_language route and Babel locale selector
supported_languages = ["en", "zh_Hans_CN"]

def get_locale():
    # Returns the language stored in session, defaults to English
    return session.get("lang", "en")

# Initialise extensions
babel = Babel(app, locale_selector=get_locale)
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

# ── Flask-Login Setup ────────────────────────────────────────────────────────
# Redirects unauthenticated users to the volunteer (login/signup) page
login_manager = LoginManager(app)
login_manager.login_view = "volunteer"

@login_manager.user_loader
def load_user(user_id):
    # Tells Flask-Login how to reload the user object from the session
    return db.session.get(User, int(user_id))

# Create all database tables on startup if they don't already exist
#with app.app_context():
#    db.create_all()

# ── Context Processor: inject language info into all templates ───────────────
@app.context_processor
def inject_language():
    language_names = {
        "en": "English",
        "zh_Hans_CN": "中文"
    }
    current_lang = session.get("lang", "en")
    return {
        "current_lang": current_lang,
        "current_language_name": language_names.get(current_lang, "English")
    }

# ── Page Routes ──────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html", page_name="home")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/stories")
def stories():
    return render_template("stories.html")

@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/donate")
def donate():
    return render_template("donate.html")

@app.route("/set-language/<lang>")
def set_language(lang):
    # Saves the selected language in session and redirects back to the same page
    if lang in supported_languages:
        session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

@app.route("/volunteer")
def volunteer():
    # Renders the combined login/signup page (volunteer portal)
    return render_template("volunteer.html")
@app.route("/login", methods=["POST"])
def login():
    """
    Handles volunteer login.
    """

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return render_template(
            "volunteer.html",
            error="Invalid email or password."
        )

    login_user(user)

    session["user_name"] = user.full_name
    session["user_role"] = user.role
    session["user_email"] = user.email

    return redirect(url_for("dashboard"))
# ── Signup Route ─────────────────────────────────────────────────────────────
# Handles volunteer registration with email OTP verification.
# User data is temporarily stored in session until OTP is confirmed.
# The actual User record is only created after successful OTP verification.
@app.route("/signup", methods=["POST"])
def signup():
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    area = request.form.get("area", "")

    # Validate that both passwords match before proceeding
    if password != confirm_password:
        return render_template("volunteer.html", error="Passwords do not match.", show_signup=True)

    # Check if an account with this email already exists in the database
    if User.query.filter_by(email=email).first():
        return render_template("volunteer.html", error="An account with this email already exists.", show_signup=True)

    # Generate a 6-digit OTP and store it in session with a timestamp
    otp = str(random.randint(100000, 999999))
    session["otp"] = otp
    session["otp_created_at"] = datetime.now(timezone.utc).isoformat()

    # Temporarily store user details in session — saved to DB only after OTP is verified and this is user session stored in browser cookie
    session["pending_user"] = {
        "full_name": f"{first_name} {last_name}",
        "email": email,
        "phone": phone or "0000000000",
        "area": area,
        "password": password,
    }

    # Send OTP email to the user via Gmail SMTP
    msg = Message(
        subject="WMAA — Your Verification Code",
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )
    msg.body = f"Hi {first_name},\n\nYour WMAA verification code is: {otp}\n\nThis code expires in 10 minutes.\n\nWMAA Team"
    mail.send(msg)

    return redirect(url_for("verify_otp"))

# OTP Verification Route
# Validates the OTP entered by the user.
# On success: creates the User record in the database and clears the session.
# On failure: shows an error and lets the user try again.
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered = request.form.get("otp", "").strip()
        stored_otp = session.get("otp")
        created_at = session.get("otp_created_at")
        pending = session.get("pending_user")

        # Guard: session may have expired or user navigated directly to this page
        if not stored_otp or not pending:
            return render_template("verify-otp.html", error="Session expired. Please sign up again.")

        # Check OTP has not expired (10 minute window)
        created_dt = datetime.fromisoformat(created_at)
        elapsed = (datetime.now(timezone.utc) - created_dt).total_seconds()
        if elapsed > 600:
            session.pop("otp", None)
            session.pop("pending_user", None)
            return render_template("verify-otp.html", error="OTP expired. Please sign up again.")

        # Check the entered OTP matches the one stored in session
        if entered != stored_otp:
            return render_template("verify-otp.html", error="Invalid OTP. Please try again.")

        # OTP is valid — create the user in the database
        new_user = User(
            full_name=pending["full_name"],
            email=pending["email"],
            phone_number=pending["phone"],
            role="volunteer",           # All self-registered users are volunteers by default
            availability=pending["area"],
        )
        new_user.set_password(pending["password"])  # Hashes password using werkzeug

        try:
            db.session.add(new_user)
            db.session.commit()

            # Clear all OTP/pending data from session after successful registration
            session.pop("otp", None)
            session.pop("otp_created_at", None)
            session.pop("pending_user", None)

            return render_template("volunteer.html", success="Account created! You can now log in.")
        except Exception:
            db.session.rollback()
            return render_template("verify-otp.html", error="Something went wrong. Please try again.")

    return render_template("verify-otp.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html")

@app.route("/vol-dashboard")
@login_required
def dashboard():
    user = {
        "name": current_user.full_name,
        "role": current_user.role
    }
    return render_template("vol-dashboard.html", user=user)

@app.route("/volunteer-schedule")
@login_required
def volunteer_schedule():
    return render_template("volunteer-schedule.html")

@app.route("/volunteer-tasks")
@login_required
def volunteer_tasks():
    return render_template("volunteer-tasks.html")

@app.route("/volunteer-events")
@login_required
def volunteer_events():
    return render_template("volunteer-events.html")

@app.route("/volunteer-profile")
@login_required
def volunteer_profile():
    user = {
        "name": current_user.full_name,
        "role": current_user.role,
        "email": current_user.email,
        "phone": current_user.phone_number,
        "availability": current_user.availability
    }
    return render_template("volunteer-profile.html", user=user)

@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("volunteer"))
    
@app.route("/api/volunteer/dashboard-stats/<int:volunteer_id>", methods=["GET"])
@login_required
def volunteer_dashboard_stats(volunteer_id):
    """
    Returns dashboard statistics for a volunteer.
    """

    stats = get_dashboard_statistics(volunteer_id)

    return {
        "success": True,
        "data": stats
    }, 200

@app.route("/api/volunteer/schedule/<int:volunteer_id>", methods=["GET"])
@login_required
def volunteer_schedule_api(volunteer_id):
    """
    Returns volunteer schedule data.
    """

    schedules = get_volunteer_schedule(volunteer_id)

    return {
        "success": True,
        "data": schedules
    }, 200

@app.route("/api/volunteer/availability/<int:volunteer_id>", methods=["GET"])
@login_required
def volunteer_availability_api(volunteer_id):
    """
    Returns volunteer availability data.
    """

    availability = VolunteerAvailability.query.filter_by(
        volunteer_id=volunteer_id
    ).order_by(
        VolunteerAvailability.available_date.desc()
    ).all()

    data = []

    for item in availability:
        data.append({
            "id": item.id,
            "available_date": item.available_date.strftime("%d %b %Y"),
            "start_time": item.start_time.strftime("%I:%M %p"),
            "end_time": item.end_time.strftime("%I:%M %p"),
            "estimated_hours": item.estimated_hours
        })

    return {
        "success": True,
        "data": data
    }, 200

@app.route("/api/volunteer/availability", methods=["POST"])
@login_required
def save_volunteer_availability():
    """
    Saves volunteer availability to database.
    """

    try:
        data = request.get_json()

        availability = VolunteerAvailability(
            volunteer_id=current_user.id,
            available_date=datetime.strptime(
                data["available_date"],
                "%Y-%m-%d"
            ).date(),
            start_time=datetime.strptime(
                data["start_time"],
                "%H:%M"
            ).time(),
            end_time=datetime.strptime(
                data["end_time"],
                "%H:%M"
            ).time(),
            estimated_hours=float(data["estimated_hours"]),
            notes=data.get("notes", ""),
            shift_type=data.get("shift_type", "General")
        )

        db.session.add(availability)
        db.session.flush()

        volunteer_hours = VolunteerHours(
            volunteer_id=current_user.id,
            schedule_id=availability.id,
            hours_completed=float(data["estimated_hours"]),
            approval_status="Pending"
        )

        db.session.add(volunteer_hours)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Availability saved and pending volunteer hours created"
        }), 201

    except Exception as e:
        db.session.rollback()

        print("SAVE AVAILABILITY ERROR:")
        traceback.print_exc()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route("/api/volunteer/register-interest", methods=["POST"])
@login_required
def register_interest():
    """
    Stores volunteer interest for an event.
    """

    data = request.get_json()

    event_name = data.get("event_name")
    event_date = data.get("event_date")

    existing_interest = VolunteerEventInterest.query.filter_by(
        volunteer_id=current_user.id,
        event_name=event_name,
        event_date=datetime.strptime(event_date, "%Y-%m-%d").date()
    ).first()

    if existing_interest:
        return {
            "success": False,
            "message": "Interest already registered"
        }, 400

    new_interest = VolunteerEventInterest(
        volunteer_id=current_user.id,
        event_name=event_name,
        event_date=datetime.strptime(event_date, "%Y-%m-%d").date()
    )

    db.session.add(new_interest)
    db.session.commit()

    return {
        "success": True,
        "message": "Interest registered successfully"
    }, 201

@app.route("/api/volunteer/hours", methods=["GET"])
@login_required
def volunteer_hours_api():
    """
    Returns volunteer hours data.
    """

    data = get_volunteer_hours(current_user.id)

    return {
        "success": True,
        "data": data
    }, 200 

if __name__ == "__main__":
    app.run(debug=True)



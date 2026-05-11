import os
import random
from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from flask import Flask, render_template, session, redirect, request, url_for
from flask_babel import Babel, gettext as _
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message

from models import db, User

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "fallback_only_for_dev")

app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wmaa.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "harpreetvallah2@gmail.com")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "owoz huca itgc zvqj")
app.config["MAIL_DEFAULT_SENDER"] = ("WMAA Charity", "harpreetvallah2@gmail.com")

supported_languages = ["en", "zh_Hans_CN"]


def get_locale():
    return session.get("lang", "en")


babel = Babel(app, locale_selector=get_locale)
db.init_app(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

login_manager = LoginManager(app)
login_manager.login_view = "volunteer"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


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
    if lang in supported_languages:
        session["lang"] = lang
    return redirect(request.referrer or url_for("home"))


@app.route("/volunteer")
def volunteer():
    return render_template("volunteer.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return render_template(
            "volunteer.html",
            error="Invalid email or password.",
            show_signup=False
        )

    if not user.is_active:
        return render_template(
            "volunteer.html",
            error="This account has been deactivated.",
            show_signup=False
        )

    login_user(user)

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    session["user_name"] = user.full_name
    session["user_role"] = user.role
    session["user_email"] = user.email

    return redirect(url_for("dashboard"))


@app.route("/signup", methods=["POST"])
def signup():
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    area = request.form.get("area", "")

    if password != confirm_password:
        return render_template("volunteer.html", error="Passwords do not match.", show_signup=True)

    if User.query.filter_by(email=email).first():
        return render_template("volunteer.html", error="An account with this email already exists.", show_signup=True)

    otp = str(random.randint(100000, 999999))
    session["otp"] = otp
    session["otp_created_at"] = datetime.now(timezone.utc).isoformat()

    session["pending_user"] = {
        "full_name": f"{first_name} {last_name}",
        "email": email,
        "phone": phone or "0000000000",
        "area": area,
        "password": password,
    }

    msg = Message(
        subject="WMAA — Your Verification Code",
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )
    msg.body = f"Hi {first_name},\n\nYour WMAA verification code is: {otp}\n\nThis code expires in 10 minutes.\n\nWMAA Team"
    mail.send(msg)

    return redirect(url_for("verify_otp"))


@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered = request.form.get("otp", "").strip()
        stored_otp = session.get("otp")
        created_at = session.get("otp_created_at")
        pending = session.get("pending_user")

        if not stored_otp or not pending:
            return render_template("verify-otp.html", error="Session expired. Please sign up again.")

        created_dt = datetime.fromisoformat(created_at)
        elapsed = (datetime.now(timezone.utc) - created_dt).total_seconds()

        if elapsed > 600:
            session.pop("otp", None)
            session.pop("pending_user", None)
            return render_template("verify-otp.html", error="OTP expired. Please sign up again.")

        if entered != stored_otp:
            return render_template("verify-otp.html", error="Invalid OTP. Please try again.")

        new_user = User(
            full_name=pending["full_name"],
            email=pending["email"],
            phone_number=pending["phone"],
            role="volunteer",
            availability=pending["area"],
        )
        new_user.set_password(pending["password"])

        try:
            db.session.add(new_user)
            db.session.commit()

            session.pop("otp", None)
            session.pop("otp_created_at", None)
            session.pop("pending_user", None)

            return render_template("volunteer.html", success="Account created! You can now log in.")
        except Exception:
            db.session.rollback()
            return render_template("verify-otp.html", error="Something went wrong. Please try again.")

    return render_template("verify-otp.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user = User.query.filter_by(email=email).first()

        generic_message = "If an account with that email exists, a password reset link has been sent."

        if user:
            token = serializer.dumps(user.email, salt="password-reset-salt")
            reset_link = url_for("reset_password", token=token, _external=True)

            msg = Message(
                subject="WMAA — Password Reset Request",
                sender=app.config["MAIL_USERNAME"],
                recipients=[user.email]
            )
            msg.body = f"""Hi {user.full_name},

We received a request to reset your WMAA account password.

Click the link below to reset your password:
{reset_link}

This link will expire in 30 minutes.

If you did not request this, you can ignore this email.

WMAA Team
"""
            mail.send(msg)

        return render_template("forgot-password.html", success=generic_message)

    return render_template("forgot-password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = serializer.loads(
            token,
            salt="password-reset-salt",
            max_age=1800
        )
    except SignatureExpired:
        return render_template(
            "forgot-password.html",
            error="This password reset link has expired. Please request a new one."
        )
    except BadSignature:
        return render_template(
            "forgot-password.html",
            error="Invalid password reset link. Please request a new one."
        )

    user = User.query.filter_by(email=email).first()

    if not user:
        return render_template(
            "forgot-password.html",
            error="Invalid password reset link. Please request a new one."
        )

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            return render_template(
                "reset-password.html",
                error="Passwords do not match."
            )

        user.set_password(password)
        db.session.commit()

        return render_template(
            "volunteer.html",
            success="Password reset successful. You can now log in."
        )

    return render_template("reset-password.html")


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
        "email": current_user.email
    }

    return render_template("volunteer-profile.html", user=user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
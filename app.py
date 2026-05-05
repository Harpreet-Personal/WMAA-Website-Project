import os
from flask import Flask, render_template, session, redirect, request, url_for
from flask_babel import Babel, gettext as _
from models import db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_only_for_dev")

app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wmaa.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

supported_languages = ["en", "zh_Hans_CN"]

def get_locale():
    return session.get("lang", "en")

babel = Babel(app, locale_selector=get_locale)
db.init_app(app)

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

@app.route("/donate", methods=["GET", "POST"])
def donate():
    if request.method == "POST":
        donor_name = request.form.get("donor_name")
        donor_email = request.form.get("donor_email")
        amount = request.form.get("amount")

        donation_data = {
            "donor_name": donor_name,
            "donor_email": donor_email,
            "amount": amount,
            "status": "Successful"
        }

        return render_template("donation-success.html", donation=donation_data)

    return render_template("donate.html")

@app.route("/set-language/<lang>")
def set_language(lang):
    if lang in supported_languages:
        session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

@app.route("/volunteer")
def volunteer():
    return render_template("volunteer.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html")

@app.route("/dashboard")
def dashboard():
    user = {
        "name": "Neha",
        "role": "volunteer"
    }

    upcoming_events = [
        {
            "title": "Community Food Drive",
            "date": "12 April 2026",
            "location": "Perth Community Centre",
            "description": "Help distribute food packs to families in need."
        },
        {
            "title": "Cultural Support Workshop",
            "date": "18 April 2026",
            "location": "Northbridge Hall",
            "description": "Assist with workshop coordination and attendee support."
        }
    ]

    return render_template("dashboard.html", user=user, upcoming_events=upcoming_events)

if __name__ == "__main__":
    app.run(debug=True)
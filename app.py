import os
from flask import Flask, render_template, session, redirect, request, url_for, flash
from flask_babel import Babel, gettext as _
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "wmaa_dev_key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wmaa.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"

supported_languages = ["en", "zh_Hans_CN"]

def get_locale():
    return session.get("lang", "en")

babel = Babel(app, locale_selector=get_locale)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "volunteer"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    return render_template("index.html", page_name='home')

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

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    flash("You have been signed out successfully.", "success")
    return redirect(url_for("home"))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
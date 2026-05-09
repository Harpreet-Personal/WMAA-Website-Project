import os
import random
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, render_template, session, redirect, request, url_for
from flask_babel import Babel, gettext as _
from flask_login import LoginManager
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

from models import db, User, Event, NewsArticle, Story, Service, HomeContent, Payment

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_only_for_dev")

# ── Config ────────────────────────────────────────────────────────────────────
app.config["BABEL_DEFAULT_LOCALE"]        = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"
app.config["SQLALCHEMY_DATABASE_URI"]     = "sqlite:///wmaa.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"]         = "smtp.gmail.com"
app.config["MAIL_PORT"]           = 587
app.config["MAIL_USE_TLS"]        = True
app.config["MAIL_USERNAME"]       = os.environ.get("MAIL_USERNAME", "harpreetvallah2@gmail.com")
app.config["MAIL_PASSWORD"]       = os.environ.get("MAIL_PASSWORD", "owoz huca itgc zvqj")
app.config["MAIL_DEFAULT_SENDER"] = ("WMAA Charity", "harpreetvallah2@gmail.com")

# Image upload folder — lives inside static/ so Flask serves it automatically
UPLOAD_FOLDER      = os.path.join("static", "images", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

supported_languages = ["en", "zh_Hans_CN"]

# ── Extensions ────────────────────────────────────────────────────────────────
def get_locale():
    return session.get("lang", "en")

babel = Babel(app, locale_selector=get_locale)
db.init_app(app)
mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = "volunteer"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create all tables on startup
with app.app_context():
    db.create_all()

# ── Helpers ───────────────────────────────────────────────────────────────────
def save_image(file_obj, subfolder="general"):
    """
    Save an uploaded image to static/images/uploads/<subfolder>/ and
    return the URL path string.  Returns None if nothing was uploaded.
    """
    if not file_obj or file_obj.filename == "":
        return None
    ext = file_obj.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    folder = os.path.join(UPLOAD_FOLDER, subfolder)
    os.makedirs(folder, exist_ok=True)
    # Timestamp suffix prevents filename collisions
    ts       = str(int(datetime.now().timestamp()))
    name     = secure_filename(file_obj.filename.rsplit(".", 1)[0])
    filename = f"{name}_{ts}.{ext}"
    file_obj.save(os.path.join(folder, filename))
    return f"/static/images/uploads/{subfolder}/{filename}"


# ── Context Processor ─────────────────────────────────────────────────────────
@app.context_processor
def inject_language():
    language_names = {"en": "English", "zh_Hans_CN": "中文"}
    current_lang   = session.get("lang", "en")
    return {
        "current_lang":          current_lang,
        "current_language_name": language_names.get(current_lang, "English"),
    }


# ── Admin Auth Decorator ──────────────────────────────────────────────────────
def admin_required(f):
    """Redirect to /admin/login if no admin session exists."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect("/admin/login")
        return f(*args, **kwargs)
    return decorated


# =============================================================================
# PUBLIC ROUTES  — query the DB so admin changes show up immediately
# =============================================================================

@app.route("/")
def home():
    # Pass HomeContent row (or None) — index.html uses it with | default()
    hc = HomeContent.query.first()
    return render_template("index.html", page_name="home", home_content=hc)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    # If the DB has service rows, pass them; otherwise the template uses hardcoded fallback
    service_list = Service.query.order_by(Service.id).all()
    return render_template("services.html", services=service_list)


@app.route("/stories")
def stories():
    story_list = Story.query.order_by(Story.created_at.desc()).all()
    return render_template("stories.html", stories=story_list)


@app.route("/events")
def events():
    upcoming = Event.query.filter_by(event_type="upcoming").order_by(Event.date).all()
    past     = Event.query.filter_by(event_type="past").order_by(Event.date.desc()).all()
    return render_template("events.html", upcoming_events=upcoming, past_events=past)


@app.route("/news")
def news():
    articles = NewsArticle.query.order_by(NewsArticle.created_at.desc()).all()
    return render_template("news.html", news_articles=articles)


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


# ── Signup ────────────────────────────────────────────────────────────────────
@app.route("/signup", methods=["POST"])
def signup():
    first_name       = request.form.get("first_name", "").strip()
    last_name        = request.form.get("last_name",  "").strip()
    email            = request.form.get("email",    "").strip()
    phone            = request.form.get("phone",    "").strip()
    password         = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    area             = request.form.get("area", "")

    if password != confirm_password:
        return render_template("volunteer.html", error="Passwords do not match.", show_signup=True)
    if User.query.filter_by(email=email).first():
        return render_template("volunteer.html", error="An account with this email already exists.", show_signup=True)

    otp = str(random.randint(100000, 999999))
    session["otp"]            = otp
    session["otp_created_at"] = datetime.now(timezone.utc).isoformat()
    session["pending_user"]   = {
        "full_name": f"{first_name} {last_name}",
        "email":     email,
        "phone":     phone or "0000000000",
        "area":      area,
        "password":  password,
    }

    msg = Message(
        subject    = "WMAA — Your Verification Code",
        sender     = app.config["MAIL_USERNAME"],
        recipients = [email],
    )
    msg.body = (
        f"Hi {first_name},\n\n"
        f"Your WMAA verification code is: {otp}\n\n"
        f"This code expires in 10 minutes.\n\nWMAA Team"
    )
    mail.send(msg)
    return redirect(url_for("verify_otp"))


# ── OTP Verification ──────────────────────────────────────────────────────────
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered    = request.form.get("otp", "").strip()
        stored_otp = session.get("otp")
        created_at = session.get("otp_created_at")
        pending    = session.get("pending_user")

        if not stored_otp or not pending:
            return render_template("verify-otp.html", error="Session expired. Please sign up again.")

        created_dt = datetime.fromisoformat(created_at)
        elapsed    = (datetime.now(timezone.utc) - created_dt).total_seconds()
        if elapsed > 600:
            session.pop("otp", None)
            session.pop("pending_user", None)
            return render_template("verify-otp.html", error="OTP expired. Please sign up again.")

        if entered != stored_otp:
            return render_template("verify-otp.html", error="Invalid OTP. Please try again.")

        new_user = User(
            full_name    = pending["full_name"],
            email        = pending["email"],
            phone_number = pending["phone"],
            role         = "volunteer",
            availability = pending["area"],
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


@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html")


@app.route("/vol-dashboard")
def dashboard():
    user = {"name": session.get("user_name", "Volunteer"), "role": session.get("user_role", "volunteer")}
    return render_template("vol-dashboard.html", user=user)


@app.route("/volunteer-schedule")
def volunteer_schedule():
    user = {"name": session.get("user_name", "Volunteer")}
    return render_template("volunteer-schedule.html", user=user)


@app.route("/volunteer-tasks")
def volunteer_tasks():
    user = {"name": session.get("user_name", "Volunteer")}
    return render_template("volunteer-tasks.html", user=user)


@app.route("/volunteer-events")
def volunteer_events():
    user    = {"name": session.get("user_name", "Volunteer")}
    events  = Event.query.filter_by(event_type="upcoming").order_by(Event.date).all()
    return render_template("volunteer-events.html", user=user, events=events)


@app.route("/volunteer-profile")
def volunteer_profile():
    user = {
        "name":  session.get("user_name",  "Volunteer"),
        "role":  session.get("user_role",  "volunteer"),
        "email": session.get("user_email", "volunteer@email.com"),
    }
    return render_template("volunteer-profile.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("volunteer"))


# =============================================================================
# ADMIN ROUTES
# =============================================================================

# ── One-time Setup Route ──────────────────────────────────────────────────────
@app.route("/admin/setup")
def admin_setup():
    """
    Creates the first admin account.
    Visit this URL ONCE, then never again (or remove the route).
    URL: http://127.0.0.1:5000/admin/setup
    """
    if User.query.filter_by(role="admin").first():
        return (
            "<h2>Admin already exists.</h2>"
            "<p>This setup page is now disabled. Delete the /admin/setup route from app.py.</p>",
            403,
        )
    admin = User(
        full_name    = "WMAA Admin",
        email        = "admin@wmaacharity.com.au",
        phone_number = "0000000000",
        role         = "admin",
        is_active    = True,
    )
    admin.set_password("WmaaAdmin2026!")
    db.session.add(admin)
    db.session.commit()
    return (
        "<h2>✅ Admin account created!</h2>"
        "<p><strong>Email:</strong> admin@wmaacharity.com.au</p>"
        "<p><strong>Password:</strong> WmaaAdmin2026!</p>"
        "<p><a href='/admin/login'>Go to Admin Login →</a></p>"
        "<p style='color:red;'><strong>Important:</strong> Change this password after first login, "
        "and remove or disable the /admin/setup route from app.py.</p>"
    )


# ── Admin Login ───────────────────────────────────────────────────────────────
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_id"):
        return redirect("/admin/dashboard")

    if request.method == "POST":
        email    = request.form.get("email",    "").strip()
        password = request.form.get("password", "")
        user     = User.query.filter_by(email=email, role="admin").first()

        if user and user.check_password(password):
            session["admin_id"]   = user.id
            session["admin_name"] = user.full_name
            return redirect("/admin/dashboard")

        return render_template("admin-login.html", error="Invalid email or password.")

    return render_template("admin-login.html")


# ── Admin Logout ──────────────────────────────────────────────────────────────
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id",   None)
    session.pop("admin_name", None)
    return redirect("/admin/login")


# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    stats = {
        "total_events":       Event.query.count(),
        "total_news":         NewsArticle.query.count(),
        "total_stories":      Story.query.count(),
        "total_volunteers":   User.query.filter_by(role="volunteer").count(),
        "pending_volunteers": User.query.filter_by(role="volunteer", is_active=False).count(),
        "total_donations":    "$0.00",  # wire up when Stripe is integrated
    }
    recent_volunteers = (
        User.query.filter_by(role="volunteer")
        .order_by(User.created_at.desc())
        .limit(5).all()
    )
    return render_template(
        "admin-dashboard.html",
        admin_name        = session.get("admin_name", "Administrator"),
        stats             = stats,
        recent_volunteers = recent_volunteers,
        recent_payments   = [],
    )


# =============================================================================
# EVENTS  (full CRUD)
# =============================================================================

@app.route("/admin/events")
@admin_required
def admin_events():
    # Pass as dicts so tojson filter works in the edit modal
    events = [e.to_dict() for e in Event.query.order_by(Event.created_at.desc()).all()]
    return render_template(
        "admin-events.html",
        admin_name = session.get("admin_name", "Administrator"),
        events     = events,
    )


@app.route("/admin/events/add", methods=["POST"])
@admin_required
def admin_events_add():
    image_url = save_image(request.files.get("image"), "events")
    event = Event(
        title       = request.form.get("title",       "").strip(),
        date        = request.form.get("date",        ""),
        time        = request.form.get("time",        ""),
        location    = request.form.get("location",    ""),
        category    = request.form.get("category",    ""),
        event_type  = request.form.get("event_type",  "upcoming"),
        description = request.form.get("description", ""),
        image_url   = image_url,
    )
    db.session.add(event)
    db.session.commit()
    return redirect("/admin/events")


@app.route("/admin/events/<int:id>/edit", methods=["POST"])
@admin_required
def admin_events_edit(id):
    event             = Event.query.get_or_404(id)
    event.title       = request.form.get("title",       "").strip()
    event.date        = request.form.get("date",        "")
    event.time        = request.form.get("time",        "")
    event.location    = request.form.get("location",    "")
    event.category    = request.form.get("category",    "")
    event.event_type  = request.form.get("event_type",  "upcoming")
    event.description = request.form.get("description", "")
    new_img = save_image(request.files.get("image"), "events")
    if new_img:
        event.image_url = new_img
    db.session.commit()
    return redirect("/admin/events")


@app.route("/admin/events/<int:id>/delete", methods=["POST"])
@admin_required
def admin_events_delete(id):
    db.session.delete(Event.query.get_or_404(id))
    db.session.commit()
    return redirect("/admin/events")


# =============================================================================
# NEWS  (full CRUD)
# =============================================================================

@app.route("/admin/news")
@admin_required
def admin_news():
    articles = [a.to_dict() for a in NewsArticle.query.order_by(NewsArticle.created_at.desc()).all()]
    return render_template(
        "admin-news.html",
        admin_name    = session.get("admin_name", "Administrator"),
        news_articles = articles,
    )


@app.route("/admin/news/add", methods=["POST"])
@admin_required
def admin_news_add():
    image_url = save_image(request.files.get("image"), "news")
    article   = NewsArticle(
        title        = request.form.get("title",        "").strip(),
        category     = request.form.get("category",     "community"),
        date         = request.form.get("date",         ""),
        excerpt      = request.form.get("excerpt",      ""),
        full_content = request.form.get("full_content", ""),
        image_url    = image_url,
    )
    db.session.add(article)
    db.session.commit()
    return redirect("/admin/news")


@app.route("/admin/news/<int:id>/edit", methods=["POST"])
@admin_required
def admin_news_edit(id):
    article              = NewsArticle.query.get_or_404(id)
    article.title        = request.form.get("title",        "").strip()
    article.category     = request.form.get("category",     "community")
    article.date         = request.form.get("date",         "")
    article.excerpt      = request.form.get("excerpt",      "")
    article.full_content = request.form.get("full_content", "")
    new_img = save_image(request.files.get("image"), "news")
    if new_img:
        article.image_url = new_img
    db.session.commit()
    return redirect("/admin/news")


@app.route("/admin/news/<int:id>/delete", methods=["POST"])
@admin_required
def admin_news_delete(id):
    db.session.delete(NewsArticle.query.get_or_404(id))
    db.session.commit()
    return redirect("/admin/news")


# =============================================================================
# STORIES  (full CRUD)
# =============================================================================

@app.route("/admin/stories")
@admin_required
def admin_stories():
    story_list = [s.to_dict() for s in Story.query.order_by(Story.created_at.desc()).all()]
    return render_template(
        "admin-stories.html",
        admin_name = session.get("admin_name", "Administrator"),
        stories    = story_list,
    )


@app.route("/admin/stories/add", methods=["POST"])
@admin_required
def admin_stories_add():
    image_url = save_image(request.files.get("image"), "stories")
    story     = Story(
        title     = request.form.get("title",    "").strip(),
        category  = request.form.get("category", "Community"),
        content   = request.form.get("content",  ""),
        image_url = image_url,
    )
    db.session.add(story)
    db.session.commit()
    return redirect("/admin/stories")


@app.route("/admin/stories/<int:id>/edit", methods=["POST"])
@admin_required
def admin_stories_edit(id):
    story          = Story.query.get_or_404(id)
    story.title    = request.form.get("title",    "").strip()
    story.category = request.form.get("category", "Community")
    story.content  = request.form.get("content",  "")
    new_img = save_image(request.files.get("image"), "stories")
    if new_img:
        story.image_url = new_img
    db.session.commit()
    return redirect("/admin/stories")


@app.route("/admin/stories/<int:id>/delete", methods=["POST"])
@admin_required
def admin_stories_delete(id):
    db.session.delete(Story.query.get_or_404(id))
    db.session.commit()
    return redirect("/admin/stories")

# =============================================================================
# VOLUNTEERS
# =============================================================================

@app.route("/admin/volunteers")
@admin_required
def admin_volunteers():
    vol_list = User.query.filter_by(role="volunteer").order_by(User.created_at.desc()).all()
    counts   = {
        "total":   len(vol_list),
        "active":  sum(1 for v in vol_list if v.is_active),
        "pending": sum(1 for v in vol_list if not v.is_active),
    }
    return render_template(
        "admin-volunteers.html",
        admin_name = session.get("admin_name", "Administrator"),
        volunteers = vol_list,
        counts     = counts,
    )


@app.route("/admin/volunteers/<int:id>/approve", methods=["POST"])
@admin_required
def admin_volunteers_approve(id):
    user           = User.query.get_or_404(id)
    user.is_active = True
    db.session.commit()
    return redirect("/admin/volunteers")


@app.route("/admin/volunteers/<int:id>/deactivate", methods=["POST"])
@admin_required
def admin_volunteers_deactivate(id):
    user           = User.query.get_or_404(id)
    user.is_active = False
    db.session.commit()
    return redirect("/admin/volunteers")


@app.route("/admin/volunteers/<int:id>/delete", methods=["POST"])
@admin_required
def admin_volunteers_delete(id):
    db.session.delete(User.query.get_or_404(id))
    db.session.commit()
    return redirect("/admin/volunteers")


# =============================================================================
# DONATIONS  (read-only view — wired to Stripe later)
# =============================================================================

@app.route("/admin/donations")
@admin_required
def admin_donations():
    # TODO: replace with real Payment queries once Stripe webhooks are integrated
    totals = {
        "total_amount":    "$0.00",
        "month_amount":    "$0.00",
        "total_completed": 0,
        "total_pending":   0,
    }
    return render_template(
        "admin-donations.html",
        admin_name = session.get("admin_name", "Administrator"),
        payments   = [],
        totals     = totals,
    )


# =============================================================================
if __name__ == "__main__":
    app.run(debug=True)
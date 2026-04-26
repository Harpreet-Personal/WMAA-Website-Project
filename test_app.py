import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client

# ── Route Tests ───────────────────────────────────────────

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200

def test_about_page(client):
    response = client.get("/about")
    assert response.status_code == 200

def test_services_page(client):
    response = client.get("/services")
    assert response.status_code == 200

def test_stories_page(client):
    response = client.get("/stories")
    assert response.status_code == 200

def test_events_page(client):
    response = client.get("/events")
    assert response.status_code == 200

def test_news_page(client):
    response = client.get("/news")
    assert response.status_code == 200

def test_contact_page(client):
    response = client.get("/contact")
    assert response.status_code == 200

def test_donate_page(client):
    response = client.get("/donate")
    assert response.status_code == 200

def test_volunteer_page(client):
    response = client.get("/volunteer")
    assert response.status_code == 200

def test_invalid_route(client):
    response = client.get("/this-does-not-exist")
    assert response.status_code == 404

def test_language_switch_english(client):
    response = client.get("/set-language/en")
    assert response.status_code == 302

def test_language_switch_chinese(client):
    response = client.get("/set-language/zh_Hans_CN")
    assert response.status_code == 302


# ── Language Session Tests ────────────────────────────────

def test_chinese_saved_to_session(client):
    client.get("/set-language/zh_Hans_CN")
    with client.session_transaction() as sess:
        assert sess.get("lang") == "zh_Hans_CN"

def test_english_saved_to_session(client):
    client.get("/set-language/en")
    with client.session_transaction() as sess:
        assert sess.get("lang") == "en"

def test_unsupported_language_not_saved_to_session(client):
    client.get("/set-language/fr")
    with client.session_transaction() as sess:
        assert sess.get("lang") != "fr"

def test_default_language_is_english(client):
    with client.session_transaction() as sess:
        assert sess.get("lang", "en") == "en"

def test_home_page_loads_in_chinese(client):
    with client.session_transaction() as sess:
        sess["lang"] = "zh_Hans_CN"
    response = client.get("/")
    assert response.status_code == 200

def test_about_page_loads_in_chinese(client):
    with client.session_transaction() as sess:
        sess["lang"] = "zh_Hans_CN"
    response = client.get("/about")
    assert response.status_code == 200

def test_services_page_loads_in_chinese(client):
    with client.session_transaction() as sess:
        sess["lang"] = "zh_Hans_CN"
    response = client.get("/services")
    assert response.status_code == 200

def test_contact_page_loads_in_chinese(client):
    with client.session_transaction() as sess:
        sess["lang"] = "zh_Hans_CN"
    response = client.get("/contact")
    assert response.status_code == 200

def test_donate_page_loads_in_chinese(client):
    with client.session_transaction() as sess:
        sess["lang"] = "zh_Hans_CN"
    response = client.get("/donate")
    assert response.status_code == 200

def test_events_page_loads_in_chinese(client):
    with client.session_transaction() as sess:
        sess["lang"] = "zh_Hans_CN"
    response = client.get("/events")
    assert response.status_code == 200

def test_news_page_loads_in_chinese(client):
    with client.session_transaction() as sess:
        sess["lang"] = "zh_Hans_CN"
    response = client.get("/news")
    assert response.status_code == 200

def test_stories_page_loads_in_chinese(client):
    with client.session_transaction() as sess:
        sess["lang"] = "zh_Hans_CN"
    response = client.get("/stories")
    assert response.status_code == 200

def test_volunteer_page_loads_in_chinese(client):
    with client.session_transaction() as sess:
        sess["lang"] = "zh_Hans_CN"
    response = client.get("/volunteer")
    assert response.status_code == 200



# ── Navigation Tests ──────────────────────────────────────

def test_navbar_contains_home_link(client):
    response = client.get("/")
    assert b"Home" in response.data

def test_navbar_contains_about_link(client):
    response = client.get("/")
    assert b"About Us" in response.data

def test_navbar_contains_services_link(client):
    response = client.get("/")
    assert b"Services" in response.data

def test_navbar_contains_contact_link(client):
    response = client.get("/")
    assert b"Contact Us" in response.data

def test_navbar_contains_news_link(client):
    response = client.get("/")
    assert b"News" in response.data

def test_navbar_contains_donate_button(client):
    response = client.get("/")
    assert b"Donate" in response.data

def test_navbar_contains_login_button(client):
    response = client.get("/")
    assert b"Login" in response.data

def test_navbar_contains_our_stories_link(client):
    response = client.get("/")
    assert b"Our Stories" in response.data

def test_navbar_contains_events_link_text(client):
    response = client.get("/")
    assert b"Events" in response.data

def test_navbar_contains_language_switcher(client):
    response = client.get("/")
    assert b"English" in response.data

def test_navbar_contains_wmaa_logo(client):
    response = client.get("/")
    assert b"WMAA" in response.data